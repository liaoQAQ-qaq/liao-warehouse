import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
// 确保这里引入的是 index.css (我们之前创建的样式文件)
// 如果你之前删了 App.css 这里还引用 App.css，就会白屏
import './index.css' 

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)