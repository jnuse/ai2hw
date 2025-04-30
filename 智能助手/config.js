/**
 * 全局配置文件
 */

// 开发环境配置
const DEV_CONFIG = {
  // API基础URL - 修改为实际的后端地址
  BASE_API: 'http://localhost:5000/api',
  // 不再使用模拟数据
  MOCK_ENABLED: false,
  // 调试日志
  DEBUG: true
};

// 生产环境配置
const PROD_CONFIG = {
  // API基础URL - 需要根据实际部署情况修改
  BASE_API: 'http://localhost:5000/api',
  // 不再使用模拟数据
  MOCK_ENABLED: false,
  // 调试日志
  DEBUG: false
};

// 根据环境选择配置
const ENV = process.env.NODE_ENV;
const config = ENV === 'production' ? PROD_CONFIG : DEV_CONFIG;

export default {
  // 应用名称
  APP_NAME: '智能职场助手',
  
  // API基础URL
  BASE_API: config.BASE_API,
  
  // 是否启用模拟数据
  MOCK_ENABLED: config.MOCK_ENABLED,
  
  // 调试日志
  DEBUG: config.DEBUG,
  
  // Token存储键名
  TOKEN_KEY: 'token',
  
  // 用户信息存储键名
  USER_INFO_KEY: 'userInfo',
  
  // 历史记录存储键名
  HISTORY_KEY: 'chatHistory',
  
  // Token过期时间（小时）
  TOKEN_EXPIRE_HOURS: 24
};
