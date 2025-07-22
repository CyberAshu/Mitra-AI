# MITRA AI Desktop Dashboard

A native desktop application for the MITRA AI personal assistant, designed to run as a persistent, always-on-top window. The dashboard displays real-time system metrics, AI activity, and user interactions using React, Tailwind CSS, and Electron.

## Features

- **Always-On-Top Desktop Dashboard**: Fixed-size window (1280x720px) that stays visible
- **Real-Time System Monitoring**: CPU, GPU, RAM usage and temperature monitoring
- **AI Core Display**: Central visual indicator with dynamic status and glow effects
- **System Tray Integration**: Minimize to tray with context menu options
- **Data Logs Viewer**: Toggleable log viewer with filtering (Ctrl+` or Cmd+`)
- **Voice Command Overlay**: Visual feedback for voice interactions
- **Dynamic Health Theming**: Color-coded interface based on system health
- **Frameless Window**: Modern, sleek appearance with custom drag regions

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Compatible with Windows, macOS, and Linux

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mitra-ai-dashboard
```

2. Install dependencies:
```bash
npm install
```

## Development

To run the application in development mode:

```bash
# Start the React development server and Electron app
npm run electron-dev
```

This will:
- Start the React development server on localhost:3000
- Launch the Electron desktop application
- Enable hot reloading for development

## Building for Production

### Build React App
```bash
npm run build
```

### Create Desktop Application
```bash
# Build for current platform
npm run dist

# Or use electron-builder directly
npm run electron-pack
```

## Architecture

### Main Components

- **AiCoreDisplay**: Central AI status indicator with animations
- **SystemMetrics**: Real-time CPU, GPU, RAM, and temperature bars
- **SystemInfo**: Network stats, uptime, and system information
- **LeftPanel**: System logs and service status
- **RightPanel**: Camera feed and process monitoring
- **AlertsStrip**: Scrollable system alerts
- **VoiceOverlay**: Voice command status indicator
- **DataLogs**: Toggleable log viewer with filtering

### System Integration

- **Electron Main Process**: Window management, system tray, IPC
- **System Information**: Real-time metrics via `systeminformation` package
- **IPC Communication**: Secure communication between React and Electron
- **Global Shortcuts**: Keyboard shortcuts for log viewer toggle

## Configuration

### Window Settings
- Size: 1280x720px (configurable)
- Always on top: Enabled by default
- Frameless: Modern appearance
- Non-resizable: Consistent dashboard experience

### System Health States
- **Healthy**: Green indicators (temp < 65°C)
- **Warming**: Yellow indicators (temp 65-75°C)
- **Overheating**: Red indicators (temp > 75°C)
- **Syncing**: Blue indicators (during operations)

## Keyboard Shortcuts

- **Ctrl+`** (or **Cmd+`** on Mac): Toggle Data Logs viewer
- **Double-click tray icon**: Show/hide application

## Customization

### Themes
The dashboard uses dynamic theming based on system health. Colors are automatically applied to:
- AI Core border and glow effects
- System metric progress bars
- Alert indicators
- Log viewer accents

### System Monitoring
Real-time data includes:
- CPU usage and model information
- Memory usage and availability
- GPU information (when available)
- System temperature monitoring
- Network statistics
- Process information

## Troubleshooting

### Common Issues

1. **Application won't start in development**:
   - Ensure all dependencies are installed: `npm install`
   - Check that ports 3000 is available
   - Verify Electron is properly installed

2. **System metrics not showing**:
   - The app falls back to simulated data in web browsers
   - Real metrics only work in the Electron desktop app

3. **Window not staying on top**:
   - Use tray menu option "Toggle Always On Top"
   - Check system permissions for window management

### Development Tips

- Use developer tools in Electron: The main process opens DevTools automatically in development
- Hot reloading: React changes are automatically reflected
- Electron restart: Required for main process changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test in both development and production builds
5. Submit a pull request

## License

This project is licensed under the MIT License.

---

Built with ❤️ using React, Electron, and Tailwind CSS

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
