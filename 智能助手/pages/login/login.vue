<template>
  <view class="login-container">
    <!-- 导航栏 -->
    <view class="navbar">
      <view class="navbar-left"></view>
      <text class="navbar-title">智能职场助手</text>
      <view class="navbar-right"></view>
    </view>
    
    <view class="logo-area">
      <image class="logo" src="/static/images/logo.png" mode="aspectFit"></image>
      <text class="title">智能职场助手</text>
    </view>
    
    <view class="form-area">
      <view class="input-item">
        <input type="text" v-model="username" placeholder="请输入用户名" placeholder-class="input-placeholder" />
      </view>
      
      <view class="input-item">
        <input type="password" v-model="password" placeholder="请输入密码" placeholder-class="input-placeholder" />
      </view>
      
      <button class="login-btn" @click="handlePasswordLogin">登录</button>
      
      <button class="wechat-btn" @click="handleWechatLogin">
        <text class="wechat-icon">微信</text>
        一键微信登录
      </button>
      
      <view class="tips">登录即表示同意《用户协议》和《隐私政策》</view>
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
      username: '',
      password: ''
    }
  },
  methods: {
    // 账号密码登录
    handlePasswordLogin() {
      if (!this.username.trim()) {
        uni.showToast({
          title: '用户名不能为空',
          icon: 'none'
        });
        return;
      }
      
      if (!this.password.trim()) {
        uni.showToast({
          title: '密码不能为空',
          icon: 'none'
        });
        return;
      }
      
      // 显示加载中
      uni.showLoading({
        title: '登录中...'
      });
      
      // 调用登录API
      request.post('/login', {
        username: this.username,
        password: this.password
      }).then(res => {
        // 隐藏加载
        uni.hideLoading();
        
        // 保存用户信息和token
        uni.setStorageSync(config.TOKEN_KEY, res.token);
        storage.user.setUserInfo(res.user);
        
        // 跳转到聊天页面
        uni.reLaunch({
          url: '/pages/chat/chat'
        });
      }).catch(err => {
        uni.hideLoading();
        uni.showToast({
          title: err.message || '登录失败，请检查用户名和密码',
          icon: 'none'
        });
      });
    },
    
    // 微信登录
    handleWechatLogin() {
      // 显示加载
      uni.showLoading({
        title: '微信登录中...'
      });
      
      // 微信小程序环境下，获取微信登录凭证
      uni.login({
        provider: 'weixin',
        success: (loginRes) => {
          // 获取到code后调用后端微信登录接口
          request.post('/login/wechat', {
            code: loginRes.code
          }).then(res => {
            // 隐藏加载
            uni.hideLoading();
            
            // 保存用户信息和token
            uni.setStorageSync(config.TOKEN_KEY, res.token);
            storage.user.setUserInfo(res.user);
            
            // 跳转到聊天页面
            uni.reLaunch({
              url: '/pages/chat/chat'
            });
          }).catch(err => {
            uni.hideLoading();
            uni.showToast({
              title: err.message || '微信登录失败',
              icon: 'none'
            });
          });
        },
        fail: () => {
          uni.hideLoading();
          uni.showToast({
            title: '获取微信授权失败',
            icon: 'none'
          });
        }
      });
    }
  }
}
</script>

<style>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50rpx;
  height: 100vh;
  background-color: #ffffff;
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
}

.navbar-title {
  flex: 1;
  text-align: center;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: calc(43px + 90rpx + 60rpx); /* 系统状态栏 + 导航栏高度 + 额外间距 */
  margin-bottom: 80rpx;
}

.logo {
  width: 180rpx;
  height: 180rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-top: 20rpx;
}

.form-area {
  width: 100%;
}

.input-item {
  background-color: #f5f5f5;
  border-radius: 12rpx;
  padding: 20rpx 30rpx;
  margin-bottom: 40rpx;
}

.input-placeholder {
  color: #999;
}

.login-btn {
  width: 100%;
  height: 90rpx;
  background-color: #1565C0;
  color: white;
  border-radius: 12rpx;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
}

.wechat-btn {
  width: 100%;
  height: 90rpx;
  background-color: #07C160;
  color: white;
  border-radius: 12rpx;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wechat-icon {
  margin-right: 10rpx;
  font-weight: bold;
}

.tips {
  font-size: 24rpx;
  color: #999;
  text-align: center;
  margin-top: 30rpx;
}
</style>
