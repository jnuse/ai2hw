/**
 * 本地存储工具类
 */
import config from '../config.js';

// 带过期时间的存储
const setStorageWithExpire = (key, value, expireHours = 24) => {
  const data = {
    value,
    expire: Date.now() + expireHours * 60 * 60 * 1000
  };
  uni.setStorageSync(key, JSON.stringify(data));
};

// 获取存储数据，自动处理过期情况
const getStorageWithExpire = (key) => {
  const dataStr = uni.getStorageSync(key);
  if (!dataStr) return null;
  
  try {
    const data = JSON.parse(dataStr);
    if (data.expire && data.expire < Date.now()) {
      uni.removeStorageSync(key);
      return null;
    }
    return data.value;
  } catch (e) {
    // 兼容非JSON格式的数据
    return dataStr;
  }
};

// 用户相关存储
const user = {
  // 保存用户信息
  setUserInfo(userInfo) {
    uni.setStorageSync(config.USER_INFO_KEY, userInfo);
  },
  
  // 获取用户信息
  getUserInfo() {
    return uni.getStorageSync(config.USER_INFO_KEY);
  },
  
  // 清除用户信息
  clearUserInfo() {
    uni.removeStorageSync(config.USER_INFO_KEY);
    uni.removeStorageSync(config.TOKEN_KEY);
  },
  
  // 检查是否已登录
  isLoggedIn() {
    return !!uni.getStorageSync(config.TOKEN_KEY);
  }
};

// 聊天历史存储
const chat = {
  // 保存聊天记录
  saveChat(chatId, messages) {
    const chats = uni.getStorageSync('chatHistory') || {};
    chats[chatId] = {
      messages,
      updateTime: Date.now()
    };
    uni.setStorageSync('chatHistory', chats);
  },
  
  // 获取聊天记录
  getChat(chatId) {
    const chats = uni.getStorageSync('chatHistory') || {};
    return chats[chatId] ? chats[chatId].messages : [];
  },
  
  // 获取所有聊天记录摘要
  getChatList() {
    const chats = uni.getStorageSync('chatHistory') || {};
    return Object.keys(chats).map(id => {
      const chat = chats[id];
      // 获取第一条消息作为标题
      const title = chat.messages && chat.messages.length > 0 
        ? chat.messages[0].content.slice(0, 20) 
        : '新对话';
      
      return {
        id,
        title,
        time: formatTime(chat.updateTime),
        updateTime: chat.updateTime
      };
    }).sort((a, b) => b.updateTime - a.updateTime); // 按时间倒序
  },
  
  // 删除聊天记录
  deleteChat(chatId) {
    const chats = uni.getStorageSync('chatHistory') || {};
    if (chats[chatId]) {
      delete chats[chatId];
      uni.setStorageSync('chatHistory', chats);
      return true;
    }
    return false;
  }
};

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hour = date.getHours().toString().padStart(2, '0');
  const minute = date.getMinutes().toString().padStart(2, '0');
  
  return `${year}-${month}-${day} ${hour}:${minute}`;
};

export default {
  set: uni.setStorageSync,
  get: uni.getStorageSync,
  remove: uni.removeStorageSync,
  clear: uni.clearStorageSync,
  setWithExpire: setStorageWithExpire,
  getWithExpire: getStorageWithExpire,
  user,
  chat
};
