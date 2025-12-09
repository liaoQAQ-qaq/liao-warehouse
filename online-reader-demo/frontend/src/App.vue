<template>
  <div class="app-container">
    <header class="navbar">
      <div class="logo">📚 极简阅读 <span class="badge">Pro</span></div>
      <div class="upload-area">
        <label class="upload-btn" :class="{ 'uploading': isUploading }">
          <span v-if="!isUploading">📤 上传新书</span>
          <span v-else>🚀 上传中...</span>
          <input type="file" @change="uploadFile" accept=".txt" :disabled="isUploading" />
        </label>
      </div>
    </header>

    <main class="main-content">
      
      <TransitionGroup name="list" tag="div" class="novel-grid">
        
        <div v-for="novel in novels" :key="novel.id" class="novel-card">
          <div class="card-icon">📄</div>
          <div class="card-info">
            <h3>{{ novel.title }}</h3>
            <p>TXT 格式</p>
          </div>
          <div class="card-actions">
            <button @click="readNovel(novel.id)" class="btn-read">阅读</button>
            <button @click="deleteNovel(novel.id)" class="btn-delete">删除</button>
          </div>
        </div>

      </TransitionGroup>

      <div v-if="novels.length === 0 && !isLoading" class="empty-state">
        🍃 书架空空如也，快去上传一本吧！
      </div>
      
      <div v-if="isLoading" class="loading-state">
        🔄 数据加载中...
      </div>
    </main>

    <Transition name="fade">
      <div v-if="currentNovel" class="reader-modal" @click.self="closeReader">
        <div class="reader-content">
          <header class="reader-header">
            <h2>{{ currentNovel.title }}</h2>
            <button @click="closeReader" class="btn-close">✖</button>
          </header>
          <div class="reader-body">
            <pre>{{ currentNovel.content }}</pre>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const novels = ref([])
const currentNovel = ref(null)
const isUploading = ref(false)
const isLoading = ref(true)

const API_URL = 'http://127.0.0.1:8000'

// 获取列表
const fetchNovels = async () => {
  try {
    const res = await fetch(`${API_URL}/novels/`)
    if (res.ok) novels.value = await res.json()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

// 上传逻辑
const uploadFile = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUploading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fetch(`${API_URL}/upload/`, { method: 'POST', body: formData })
    if (res.ok) {
      await fetchNovels() // 刷新列表
    } else {
      alert("上传失败")
    }
  } catch (e) {
    alert("上传错误")
  } finally {
    isUploading.value = false
    event.target.value = '' // 清空 input
  }
}

// 删除逻辑
const deleteNovel = async (id) => {
  if (!confirm("确定要删除这本书吗？")) return

  try {
    const res = await fetch(`${API_URL}/novels/${id}`, { method: 'DELETE' })
    if (res.ok) {
      // 在前端直接移除，触发动画，不用重新请求后端
      novels.value = novels.value.filter(n => n.id !== id)
    }
  } catch (e) {
    alert("删除失败")
  }
}

// 阅读逻辑
const readNovel = async (id) => {
  try {
    const res = await fetch(`${API_URL}/novels/${id}`)
    if (res.ok) currentNovel.value = await res.json()
  } catch (e) {
    alert("打开失败")
  }
}

const closeReader = () => {
  currentNovel.value = null
}

onMounted(fetchNovels)
</script>

<style>
/* 全局重置 */
body { margin: 0; font-family: 'Inter', system-ui, sans-serif; background: #f0f2f5; color: #333; }

/* 容器布局 */
.app-container { max-width: 1000px; margin: 0 auto; padding: 20px; min-height: 100vh; }

/* 顶部导航 */
.navbar {
  display: flex; justify-content: space-between; align-items: center;
  background: white; padding: 15px 30px; border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 30px;
}
.logo { font-size: 1.5rem; font-weight: 800; color: #2c3e50; display: flex; align-items: center; gap: 10px; }
.badge { background: #3498db; color: white; font-size: 0.8rem; padding: 2px 8px; border-radius: 8px; }

/* 上传按钮 (自定义样式覆盖原生 input) */
.upload-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; padding: 10px 20px; border-radius: 50px; cursor: pointer;
  font-weight: 600; transition: transform 0.2s, box-shadow 0.2s;
  display: inline-block; position: relative; overflow: hidden;
}
.upload-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4); }
.upload-btn input { display: none; }
.upload-btn.uploading { opacity: 0.7; cursor: wait; }

/* 网格布局 */
.novel-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px;
}

/* 书籍卡片 */
.novel-card {
  background: white; border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  transition: all 0.3s ease; position: relative;
  border: 1px solid transparent; display: flex; flex-direction: column; align-items: center; text-align: center;
}
.novel-card:hover {
  transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border-color: #e0e0e0;
}
.card-icon { font-size: 3rem; margin-bottom: 10px; }
.card-info h3 { margin: 0 0 5px; font-size: 1.1rem; color: #2c3e50; }
.card-info p { margin: 0; font-size: 0.8rem; color: #95a5a6; margin-bottom: 15px; }

/* 卡片按钮 */
.card-actions { display: flex; gap: 10px; width: 100%; }
.card-actions button {
  flex: 1; padding: 8px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: background 0.2s;
}
.btn-read { background: #eafbf0; color: #27ae60; }
.btn-read:hover { background: #d4f7de; }
.btn-delete { background: #fff0f0; color: #c0392b; }
.btn-delete:hover { background: #fadbd8; }

/* 动画特效 (List Transitions) */
.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateY(30px); }
.list-leave-active { position: absolute; } /* 让删除时后面的元素平滑补位 */

/* 阅读器模态框 */
.reader-modal {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(8px);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.reader-content {
  background: #fff8dc; width: 90%; max-width: 800px; height: 85vh;
  border-radius: 12px; box-shadow: 0 25px 50px rgba(0,0,0,0.25);
  display: flex; flex-direction: column; overflow: hidden;
}
.reader-header {
  padding: 15px 20px; border-bottom: 1px solid #eaddb6; display: flex; justify-content: space-between; align-items: center; background: #fdf6e3;
}
.reader-body { flex: 1; padding: 40px; overflow-y: auto; font-size: 1.1rem; line-height: 1.8; color: #5d4037; }
.btn-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #8b4513; }

/* 模态框动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>