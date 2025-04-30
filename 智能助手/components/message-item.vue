<template>
  <view class="message-wrapper" :class="isUser ? 'message-user' : 'message-assistant'">
    <image class="avatar" :src="avatar"></image>
    <view class="message-content">
      <view class="message-bubble">
        <rich-text :nodes="formattedContent"></rich-text>
      </view>
      <text class="message-time">{{ time }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MessageItem',
  props: {
    // 消息内容
    content: {
      type: String,
      required: true
    },
    // 是否为用户发送的消息
    isUser: {
      type: Boolean,
      default: false
    },
    // 消息发送时间
    time: {
      type: String,
      default: ''
    }
  },
  computed: {
    // 头像
    avatar() {
      return this.isUser 
        ? '/static/images/user-avatar.png' 
        : '/static/images/assistant-avatar.png';
    },
    // 格式化内容，支持简单的markdown格式
    formattedContent() {
      let content = this.content;
      
      // 处理加粗
      content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // 处理链接
      content = content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color:#1565C0;text-decoration:underline;">$1</a>');
      
      // 处理换行
      content = content.replace(/\n/g, '<br>');
      
      return content;
    }
  }
}
</script>

<style>
.message-wrapper {
  display: flex;
  margin-bottom: 20rpx;
  padding: 0 20rpx;
}

.message-user {
  flex-direction: row-reverse;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background-color: #f0f0f0;
}

.message-content {
  max-width: 70%;
  margin: 0 20rpx;
  display: flex;
  flex-direction: column;
}

.message-user .message-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 20rpx;
  border-radius: 10rpx;
  word-break: break-all;
  line-height: 1.5;
}

.message-assistant .message-bubble {
  background-color: white;
  color: #333;
  border: 1px solid #eee;
}

.message-user .message-bubble {
  background-color: #1565C0;
  color: white;
}

.message-time {
  font-size: 24rpx;
  color: #999;
  margin-top: 10rpx;
}
</style>
