<template>
  <view class="debug-container">
    <view class="navbar">
      <view class="navbar-left" @click="navigateBack">
        <text class="back-icon">←</text>
      </view>
      <text class="navbar-title">历史记录调试</text>
      <view class="navbar-right"></view>
    </view>
    
    <view class="content">
      <view class="input-box">
        <input type="text" v-model="recordId" placeholder="输入记录ID" />
        <button @click="loadRecord">加载</button>
      </view>
      
      <view class="record-info" v-if="record">
        <view class="info-item">
          <text class="label">ID:</text>
          <text class="value">{{ record.id }}</text>
        </view>
        <view class="info-item">
          <text class="label">标题:</text>
          <text class="value">{{ record.title }}</text>
        </view>
        <view class="info-item">
          <text class="label">摘要:</text>
          <text class="value">{{ record.summary }}</text>
        </view>
        <view class="info-item">
          <text class="label">时间:</text>
          <text class="value">{{ record.created_at }}</text>
        </view>
        <view class="info-item content-item">
          <text class="label">内容:</text>
          <textarea class="content-value" v-model="record.content" disabled></textarea>
        </view>
        
        <button @click="parseAndShow">解析内容</button>
      </view>
      
      <view class="parsed-messages" v-if="messages.length > 0">
        <text class="section-title">解析后的消息:</text>
        <view 
          v-for="(msg, index) in messages" 
          :key="index"
          class="message-item"
          :class="msg.sender === 'user' ? 'user-msg' : 'assistant-msg'"
        >
          <text class="sender">{{ msg.sender }}</text>
          <text class="content">{{ msg.content }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request';

export default {
  data() {
    return {
      recordId: '',
      record: null,
      messages: []
    }
  },
  methods: {
    navigateBack() {
      uni.navigateBack();
    },
    
    loadRecord() {
      if (!this.recordId) {
        uni.showToast({
          title: '请输入记录ID',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({ title: '加载中...' });
      
      request.get(`/history/${this.recordId}`).then(res => {
        this.record = res;
        this.messages = [];
        uni.showToast({
          title: '加载成功',
          icon: 'success'
        });
      }).catch(err => {
        uni.showToast({
          title: '加载失败: ' + (err.message || '未知错误'),
          icon: 'none'
        });
      }).finally(() => {
        uni.hideLoading();
      });
    },
    
    parseAndShow() {
      if (!this.record || !this.record.content) {
        uni.showToast({
          title: '没有内容可解析',
          icon: 'none'
        });
        return;
      }
      
      const messages = [];
      const lines = this.record.content.split('\n\n');
      
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
        } else if (line.trim()) {
          // 处理不符合格式的行
          messages.push({
            sender: 'unknown',
            content: line
          });
        }
      }
      
      this.messages = messages;
      
      if (messages.length === 0) {
        uni.showToast({
          title: '解析结果为空',
          icon: 'none'
        });
      }
    }
  }
}
</script>

<style>
.debug-container {
  padding: 20rpx;
  padding-top: calc(43px + 90rpx + 20rpx);
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

.input-box {
  display: flex;
  margin-bottom: 20rpx;
}

.input-box input {
  flex: 1;
  border: 1px solid #ddd;
  padding: 10rpx;
  border-radius: 8rpx;
}

.input-box button {
  margin-left: 10rpx;
  background-color: #1565C0;
  color: white;
  border: none;
  border-radius: 8rpx;
  padding: 0 20rpx;
}

.record-info {
  background-color: white;
  border-radius: 8rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.info-item {
  margin-bottom: 10rpx;
  display: flex;
}

.label {
  font-weight: bold;
  width: 100rpx;
}

.value {
  flex: 1;
}

.content-item {
  flex-direction: column;
}

.content-value {
  width: 100%;
  height: 400rpx;
  border: 1px solid #ddd;
  padding: 10rpx;
  margin-top: 10rpx;
  border-radius: 8rpx;
}

.record-info button {
  margin-top: 20rpx;
  background-color: #1565C0;
  color: white;
}

.parsed-messages {
  background-color: white;
  border-radius: 8rpx;
  padding: 20rpx;
}

.section-title {
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}

.message-item {
  margin-bottom: 20rpx;
  padding: 10rpx;
  border-radius: 8rpx;
}

.user-msg {
  background-color: #e3f2fd;
}

.assistant-msg {
  background-color: #f1f8e9;
}

.sender {
  font-weight: bold;
  margin-bottom: 5rpx;
  display: block;
}

.content {
  word-break: break-all;
}
</style>
