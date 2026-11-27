/**
 * Preload script for ActionCam MCP Studio Workflow Integration Plugin.
 * Exposes both DaVinci Resolve Studio JavaScript APIs and ActionCam MCP Bridge.
 */

const { contextBridge, ipcRenderer } = require('electron/renderer');

contextBridge.exposeInMainWorld('resolveAPI', {
    // Navigation
    openPage: (pageName) => ipcRenderer.invoke('resolve:openPage', pageName),

    // Projects
    createProject: (projectName) => ipcRenderer.invoke('resolve:createProject', projectName),
    openProject: (projectName) => ipcRenderer.invoke('resolve:openProject', projectName),
    saveProject: () => ipcRenderer.invoke('resolve:saveProject'),
    getCurrentProjectName: () => ipcRenderer.invoke('resolve:getCurrentProjectName'),

    // Media Pool & Bins
    createBin: (binName) => ipcRenderer.invoke('resolve:createBin', binName),
    selectBin: (binName) => ipcRenderer.invoke('resolve:selectBin', binName),
    addClips: (filePathsArray) => ipcRenderer.invoke('resolve:addClips', filePathsArray),

    // Timelines & Cuts
    createTimeline: (timelineName) => ipcRenderer.invoke('resolve:createTimeline', timelineName),
    detectSceneCuts: () => ipcRenderer.invoke('resolve:detectSceneCuts'),
    getSceneCutStatus: () => ipcRenderer.invoke('resolve:getSceneCutStatus'),

    // Deliver & Render
    getRenderPresets: () => ipcRenderer.invoke('resolve:getRenderPresets'),
    renderTimeline: (presetName, targetDir, clipName) => ipcRenderer.invoke('resolve:renderTimeline', presetName, targetDir, clipName),

    // MCP Bridge Info
    isPluginMode: () => true,
    getPluginVersion: () => '1.0.0',
    cleanup: () => ipcRenderer.invoke('resolve:cleanup')
});

