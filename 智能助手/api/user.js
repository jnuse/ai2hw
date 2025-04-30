/**
 * 用户相关API
 */

import request from '../utils/request';

export default {
  /**
   * 用户登录
   * @param {String} username 用户名
   */
  login(username) {
    return request.post('/user/login', {
      username
    });
  },
  
  /**
   * 获取用户信息
   */
  getUserInfo() {
    return request.get('/user/info');
  },
  
  /**
   * 更新用户信息
   * @param {Object} userInfo 用户信息
   */
  updateUserInfo(userInfo) {
    return request.post('/user/update', userInfo);
  },
  
  /**
   * 退出登录
   */
  logout() {
    return request.post('/user/logout');
  }
};
