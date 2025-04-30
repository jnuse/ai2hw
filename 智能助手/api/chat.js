/**
 * 聊天相关API
 */

import request from '../utils/request';

export default {
  /**
   * 发送消息获取回复
   * @param {String} content 用户输入内容
   * @param {String} conversationId 对话ID，新对话不传
   */
  sendMessage(content, conversationId = '') {
    return request.post('/chat/send', {
      content,
      conversationId
    });
  },
  
  /**
   * 获取历史对话列表
   * @param {Number} page 页码
   * @param {Number} pageSize 每页条数
   */
  getHistoryList(page = 1, pageSize = 20) {
    return request.get('/chat/history', {
      page,
      pageSize
    });
  },
  
  /**
   * 获取对话详情
   * @param {String} conversationId 对话ID
   */
  getConversationDetail(conversationId) {
    return request.get(`/chat/detail/${conversationId}`);
  },
  
  /**
   * 删除对话
   * @param {String} conversationId 对话ID
   */
  deleteConversation(conversationId) {
    return request.delete(`/chat/delete/${conversationId}`);
  }
};
