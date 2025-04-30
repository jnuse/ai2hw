/**
 * 网络请求工具类
 */
import config from '../config.js';

// API基础URL，从配置文件中获取
const BASE_URL = config.BASE_API;

// 请求拦截器
const beforeRequest = (options) => {
  // 获取token
  const token = uni.getStorageSync(config.TOKEN_KEY);
  if (token) {
    options.header = {
      ...options.header,
      'Authorization': `Bearer ${token}`
    };
  }
  return options;
};

// 响应拦截器
const handleResponse = (res) => {
  if (res.statusCode === 200) {
    // 接口数据格式: { code: 0, data: {}, message: '' }
    if (res.data.code === 0) {
      // 确保返回的是真正的数据部分
      console.log('API返回原始数据:', res.data); // 调试日志
      return res.data.data;
    } else {
      uni.showToast({
        title: res.data.message || '请求失败',
        icon: 'none'
      });
      return Promise.reject(res.data);
    }
  } else if (res.statusCode === 401) {
    // token失效，重新登录
    uni.showToast({
      title: '登录已过期，请重新登录',
      icon: 'none'
    });
    
    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/login/login'
      });
    }, 1500);
    
    return Promise.reject(res);
  } else {
    uni.showToast({
      title: '网络错误，请稍后再试',
      icon: 'none'
    });
    return Promise.reject(res);
  }
};

// 请求函数
const request = (options) => {
  const config = beforeRequest(options);
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: config.url.startsWith('http') ? config.url : BASE_URL + config.url,
      method: config.method || 'GET',
      data: config.data || {},
      header: config.header || {},
      success: (res) => {
        try {
          const result = handleResponse(res);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 封装常用请求方法
export default {
  get(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: 'GET',
      ...options
    });
  },
  
  post(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: 'POST',
      ...options
    });
  },
  
  put(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: 'PUT',
      ...options
    });
  },
  
  delete(url, data = {}, options = {}) {
    return request({
      url,
      data,
      method: 'DELETE',
      ...options
    });
  }
};
