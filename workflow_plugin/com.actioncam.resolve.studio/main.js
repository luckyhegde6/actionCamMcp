/**
 * ActionCam MCP Studio - DaVinci Resolve Workflow Integration Plugin
 * Main Electron Process
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const WorkflowIntegration = require('./WorkflowIntegration.node');

const PLUGIN_ID = 'com.actioncam.resolve.studio';

let mainWindow = null;
let resolveObj = null;
let projectManagerObj = null;

function debugLog(msg) {
    if (mainWindow && mainWindow.webContents) {
        mainWindow.webContents.executeJavaScript(`console.log('[ActionCam Plugin Main] ${msg}');`);
    }
}

async function initResolveInterface() {
    try {
        const isSuccess = await WorkflowIntegration.Initialize(PLUGIN_ID);
        if (!isSuccess) {
            console.error('Failed to initialize WorkflowIntegration');
            return null;
        }
        resolveObj = await WorkflowIntegration.GetResolve();
        return resolveObj;
    } catch (e) {
        console.error('initResolveInterface error:', e);
        return null;
    }
}

async function getResolve() {
    if (!resolveObj) {
        resolveObj = await initResolveInterface();
    }
    return resolveObj;
}

async function getProjectManager() {
    if (!projectManagerObj) {
        const resolve = await getResolve();
        if (resolve) {
            projectManagerObj = await resolve.GetProjectManager();
        }
    }
    return projectManagerObj;
}

async function getCurrentProject() {
    const pm = await getProjectManager();
    if (pm) {
        return await pm.GetCurrentProject();
    }
    return null;
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 850,
        title: 'ActionCam MCP Studio — DaVinci Resolve Workflow Integration',
        backgroundColor: '#141619',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false,
        }
    });

    // Load either the local file or the active MCP Desktop UI
    const uiPath = path.join(__dirname, '../../actioncam_mcp/desktop_ui/index.html');
    mainWindow.loadFile(uiPath).catch(() => {
        mainWindow.loadURL('http://127.0.0.1:8765/index.html');
    });

    mainWindow.on('closed', async () => {
        mainWindow = null;
        if (WorkflowIntegration && WorkflowIntegration.CleanUp) {
            await WorkflowIntegration.CleanUp();
        }
    });
}

// App lifecycle
app.whenReady().then(async () => {
    await initResolveInterface();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

// IPC Handlers
ipcMain.handle('resolve:openPage', async (event, pageName) => {
    const resolve = await getResolve();
    if (resolve) return await resolve.OpenPage(pageName);
    return false;
});

ipcMain.handle('resolve:createProject', async (event, projectName) => {
    const pm = await getProjectManager();
    if (pm) return await pm.CreateProject(projectName);
    return null;
});

ipcMain.handle('resolve:openProject', async (event, projectName) => {
    const pm = await getProjectManager();
    if (pm) return await pm.LoadProject(projectName);
    return null;
});

ipcMain.handle('resolve:saveProject', async (event) => {
    const pm = await getProjectManager();
    if (pm) return await pm.SaveProject();
    return false;
});

ipcMain.handle('resolve:getCurrentProjectName', async (event) => {
    const proj = await getCurrentProject();
    if (proj) return await proj.GetName();
    return 'Untitled';
});

ipcMain.handle('resolve:createBin', async (event, binName) => {
    const proj = await getCurrentProject();
    if (proj) {
        const mp = await proj.GetMediaPool();
        const root = await mp.GetRootFolder();
        return await mp.AddSubFolder(root, binName);
    }
    return null;
});

ipcMain.handle('resolve:addClips', async (event, filePaths) => {
    const proj = await getCurrentProject();
    if (proj) {
        const mp = await proj.GetMediaPool();
        return await mp.ImportMedia(filePaths);
    }
    return [];
});

ipcMain.handle('resolve:createTimeline', async (event, timelineName) => {
    const proj = await getCurrentProject();
    if (proj) {
        const mp = await proj.GetMediaPool();
        return await mp.CreateEmptyTimeline(timelineName);
    }
    return null;
});

ipcMain.handle('resolve:detectSceneCuts', async (event) => {
    const proj = await getCurrentProject();
    if (proj) {
        const tl = await proj.GetCurrentTimeline();
        if (tl && tl.DetectSceneCuts) {
            return await tl.DetectSceneCuts();
        }
    }
    return false;
});

ipcMain.handle('resolve:getSceneCutStatus', async (event) => {
    const proj = await getCurrentProject();
    if (proj && proj.GetDetectSceneCutsStatus) {
        return await proj.GetDetectSceneCutsStatus();
    }
    return { JobStatus: 'Complete', CompletionPercentage: 100 };
});

ipcMain.handle('resolve:getRenderPresets', async (event) => {
    const proj = await getCurrentProject();
    if (proj) return await proj.GetRenderPresetList();
    return [];
});

ipcMain.handle('resolve:renderTimeline', async (event, presetName, targetDir, clipName) => {
    const proj = await getCurrentProject();
    if (proj) {
        if (presetName) await proj.LoadRenderPreset(presetName);
        await proj.SetRenderSettings({
            SelectAllFrames: true,
            TargetDir: targetDir,
            CustomName: clipName
        });
        const jobId = await proj.AddRenderJob();
        return await proj.StartRendering([jobId]);
    }
    return false;
});

ipcMain.handle('resolve:cleanup', async (event) => {
    if (WorkflowIntegration && WorkflowIntegration.CleanUp) {
        return await WorkflowIntegration.CleanUp();
    }
    return true;
});

