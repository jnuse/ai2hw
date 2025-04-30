<template>
  <view class="chat-container">
    <!-- 导航栏 -->
    <view class="navbar">
      <view class="navbar-left" @click="navigateBack">
        <text class="back-icon">←</text>
      </view>
      <text class="navbar-title">{{ navbarTitle }}</text>
      <view class="navbar-right"></view>
    </view>
    
    <!-- 聊天内容区域 -->
    <scroll-view class="chat-content" scroll-y="true" :scroll-into-view="scrollToView" scroll-with-animation>
      <view v-for="(item, index) in messageList" :key="index" :id="'msg-' + index">
        <view class="message-item" :class="item.sender === 'user' ? 'message-user' : 'message-assistant'">
          <image class="avatar" :src="item.sender === 'user' ? '/static/images/user-avatar.png' : '/static/images/assistant-avatar.png'"></image>
          <view class="message-bubble">{{ item.content }}</view>
        </view>
      </view>
    </scroll-view>
    
    <!-- 输入区域 -->
    <view class="input-area">
      <view class="input-box">
        <input type="text" v-model="inputMessage" placeholder="请输入您的问题" confirm-type="send" @confirm="sendMessage" />
        <button class="send-btn" @click="sendMessage">发送</button>
      </view>
      
      <!-- 底部导航 -->
      <view class="bottom-nav">
        <view class="nav-btn active" @click="navigateToChat">
          <text class="nav-text">智能问答</text>
        </view>
        <view class="nav-btn" @click="showExamples">
          <text class="nav-text">问题示例</text>
        </view>
        <view class="nav-btn" @click="navigateToHistory">
          <text class="nav-text">历史记录</text>
        </view>
      </view>
    </view>
    
    <!-- 问题示例弹窗 -->
    <view class="example-popup" v-if="showExamplesList">
      <view class="example-container">
        <view class="example-header">
          <text class="example-title">热门问题示例</text>
          <text class="example-close" @click="showExamplesList = false">×</text>
        </view>
        <scroll-view class="example-list" scroll-y>
          <view 
            v-for="(item, index) in exampleQuestions" 
            :key="index"
            class="example-item"
            @click="selectExample(item)"
          >
            {{ item }}
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request';
import storage from '../../utils/storage';
import config from '../../config';

export default {
  data() {
    return {
      inputMessage: '',
      messageList: [],
      scrollToView: '',
      conversationId: '',
      username: '',
      showExamplesList: false,
      exampleQuestions: [],
      navbarTitle: '智能职场助手',
      isLoading: false
    }
  },
  onLoad(options) {
    this.username = uni.getStorageSync('username') || '用户';
    
    // 设置当前日期时间作为标题栏内容
    this.updateNavbarTitle();
    
    // 加载示例问题
    this.loadExampleQuestions();
    
    // 检查是否从历史记录页面跳转而来
    if (options.recordId) {
      this.conversationId = options.recordId;
      this.loadHistoryConversation(options.recordId);
    } else {
      // 初始化一条欢迎消息
      this.messageList = [
        {
          sender: 'assistant',
          content: `您好，${this.username}！我是您的智能职场助手，请问有什么可以帮您的？`
        }
      ];
    }
  },
  methods: {
    // 加载示例问题
    loadExampleQuestions() {
      request.get('/examples').then(res => {
        this.exampleQuestions = res || [];
      }).catch(err => {
        console.error('获取示例问题失败:', err);
        // 使用默认示例问题
        this.exampleQuestions = [
          '如何提高工作效率？',
          '职场中如何处理人际关系？',
          '如何准备晋升答辩？',
          '如何优化我的简历？',
          '如何进行有效的时间管理？'
        ];
      });
    },
    
    updateNavbarTitle() {
      // 格式化当前日期时间
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      
      this.navbarTitle = `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    
    navigateBack() {
      uni.navigateBack();
    },
    
    sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return;
      
      // 添加用户消息
      this.messageList.push({
        sender: 'user',
        content: this.inputMessage
      });
      
      const userMessage = this.inputMessage;
      this.inputMessage = '';
      
      // 更新导航栏标题为当前时间
      this.updateNavbarTitle();
      
      // 滚动到底部
      this.scrollToBottom();
      
      // 显示加载中状态
      this.isLoading = true;
      
      // 添加临时消息，表示正在思考
      const thinkingIndex = this.messageList.length;
      this.messageList.push({
        sender: 'assistant',
        content: '思考中...'
      });
      
      // 调用聊天API
      request.post('/chat', {
        message: userMessage,
        conversationId: this.conversationId
      }).then(res => {
        // 更新会话ID - 非常重要，确保后续消息能关联到同一对话
        this.conversationId = res.record_id;
        
        // 替换"思考中"消息
        this.messageList.splice(thinkingIndex, 1, {
          sender: 'assistant',
          content: res.reply
        });
        
        // 滚动到底部
        this.scrollToBottom();
      }).catch(err => {
        // 显示错误消息
        this.messageList.splice(thinkingIndex, 1, {
          sender: 'assistant',
          content: `抱歉，发生了错误：${err.message || '未知错误'}`
        });
      }).finally(() => {
        this.isLoading = false;
      });
    },
    
    scrollToBottom() {
      this.scrollToView = `msg-${this.messageList.length - 1}`;
    },
    
    loadHistoryConversation(recordId) {
      uni.showLoading({
        title: '加载中...'
      });
      
      // 调用API获取历史对话详情
      request.get(`/history/${recordId}`).then(res => {
        console.log('历史记录详情:', res); // 调试日志，查看返回的数据结构
        
        if (res && res.content) {
          // 解析对话内容
          this.parseHistoryContent(res.content);
          
          // 设置标题，可选
          if (res.title) {
            // 更新导航栏标题，显示对话标题
            this.navbarTitle = res.title;
          }
        } else {
          uni.showToast({
            title: '历史记录内容为空',
            icon: 'none'
          });
          this.messageList = [];
        }
      }).catch(err => {
        console.error('加载历史记录失败:', err); // 调试日志，记录错误
        uni.showToast({
          title: '加载历史对话失败',
          icon: 'none'
        });
        this.messageList = [];
      }).finally(() => {
        uni.hideLoading();
      });
    },
    
    // 解析历史对话内容为消息列表
    parseHistoryContent(content) {
      if (!content) {
        this.messageList = [];
        return;
      }
      
      console.log('准备解析的历史内容:', content); // 调试日志，查看内容
      
      const messages = [];
      // 分割对话内容
      const lines = content.split('\n\n');
      
      for (const line of lines) {
        if (line.startsWith('用户: ')) {
          messages.push({
            sender: 'user',
            content: line.substring(4)
          });
        } else if (line.startsWith('助手: ')) {
          messages.push({
            sender: 'assistant',
            content: line.substring(4)
          });
        }
      }
      
      console.log('解析后的消息列表:', messages); // 调试日志，确认解析结果
      
      if (messages.length > 0) {
        this.messageList = messages;
      } else {
        // 如果解析后没有消息，尝试直接展示内容
        this.messageList = [
          {
            sender: 'assistant',
            content: '以下是历史对话记录:\n\n' + content
          }
        ];
      }
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    
    navigateToChat() {
      // 已经在聊天页面，不需要跳转
    },
    
    navigateToHistory() {
      uni.navigateTo({
        url: '/pages/history/history'
      });
    },
    
    // 显示问题示例
    showExamples() {
      this.showExamplesList = true;
    },
    
    // 选择问题示例
    selectExample(question) {
      this.inputMessage = question;
      this.showExamplesList = false;
      this.sendMessage();
    }
  }
}
</script>

<style>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f1f1f1;
}

.navbar {
  background-color: #1565C0;
  height: 90rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  font-size: 32rpx;
  position: fixed;
  top: 43px;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0 20rpx;
}

.navbar-left, .navbar-right {
  width: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 40rpx;
  font-weight: bold;
}

.navbar-title {
  flex: 1;
  text-align: center;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-content {
  flex: 1;
  padding: 20rpx;
  margin-top: calc(43px + 90rpx + 20rpx); /* 系统状态栏 + 导航栏高度 + 额外间距 */
  margin-bottom: 180rpx;
}

.message-item {
  display: flex;
  margin-bottom: 30rpx;
}

.message-user {
  flex-direction: row-reverse;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
}

.message-bubble {
  max-width: 70%;
  padding: 20rpx;
  border-radius: 10rpx;
  margin: 0 20rpx;
  word-break: break-all;
}

.message-assistant .message-bubble {
  background-color: white;
  color: #333;
}

.message-user .message-bubble {
  background-color: #1565C0;
  color: white;
}

.input-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: white;
  padding: 20rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.input-box {
  display: flex;
  background-color: #f5f5f5;
  border-radius: 10rpx;
  padding: 15rpx;
}

.input-box input {
  flex: 1;
  height: 70rpx;
}

.send-btn {
  width: 120rpx;
  height: 70rpx;
  background-color: #1565C0;
  color: white;
  font-size: 28rpx;
  margin-left: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8rpx;
}

.bottom-nav {
  display: flex;
  margin-top: 20rpx;
  border-top: 1rpx solid #eee;
  padding-top: 20rpx;
  padding-bottom: 35rpx;
}

.nav-btn {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80rpx;
  color: #666;
}

.nav-btn.active {
  color: #1565C0;
  font-weight: bold;
}

.nav-text {
  font-size: 30rpx;
}

/* 问题示例弹窗样式 */
.example-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.example-container {
  width: 90%;
  max-height: 70%;
  background-color: #fff;
  border-radius: 12rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.example-header {
  padding: 25rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid #eee;
}

.example-title {
  font-size: 32rpx;
  font-weight: bold;
}

.example-close {
  font-size: 40rpx;
  color: #999;
  padding: 0 20rpx;
}

.example-list {
  flex: 1;
  max-height: 800rpx;
}

.example-item {
  padding: 25rpx;
  border-bottom: 1rpx solid #f0f0f0;
  font-size: 30rpx;
}

.example-item:active {
  background-color: #f5f5f5;
}
</style>
