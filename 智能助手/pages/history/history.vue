<template>
  <view class="history-container">
    <!-- 导航栏 -->
    <view class="navbar">
      <view class="navbar-left" @click="navigateBack">
        <text class="back-icon">←</text>
      </view>
      <text class="navbar-title">历史记录</text>
      <view class="navbar-right"></view>
    </view>
    
    <!-- 历史记录列表 -->
    <scroll-view class="history-list" scroll-y="true" @scrolltolower="loadMoreHistory">
      <view 
        v-for="(item, index) in historyList" 
        :key="index" 
        class="history-item"
        @click="viewHistoryDetail(item.id)">
        <view class="history-content">
          <text class="history-title">{{ item.title }}</text>
          <text class="history-time">{{ item.created_at }}</text>
        </view>
        <view class="history-actions">
          <text class="history-delete" @click.stop="confirmDelete(item.id)">×</text>
          <text class="history-arrow">›</text>
        </view>
      </view>
      
      <view v-if="isLoading" class="loading-more">
        <text>加载中...</text>
      </view>
      
      <view v-if="historyList.length === 0 && !isLoading" class="empty-tip">
        <text>暂无历史记录</text>
      </view>
    </scroll-view>
    
    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-btn" @click="navigateToChat">
        <text class="nav-text">智能问答</text>
      </view>
      <view class="nav-btn active" @click="navigateToHistory">
        <text class="nav-text">历史记录</text>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request';

export default {
  data() {
    return {
      historyList: [],
      page: 1,
      pageSize: 10,
      totalCount: 0,
      isLoading: false,
      hasMore: true
    }
  },
  onLoad() {
    this.loadHistoryList();
  },
  onShow() {
    // 每次页面显示时刷新历史记录
    this.refreshHistory();
  },
  methods: {
    navigateBack() {
      uni.navigateBack();
    },
    
    // 刷新历史列表
    refreshHistory() {
      this.page = 1;
      this.historyList = [];
      this.hasMore = true;
      this.loadHistoryList();
    },
    
    // 加载历史记录
    loadHistoryList() {
      if (this.isLoading || !this.hasMore) return;
      
      this.isLoading = true;
      
      // 调用API获取历史记录
      request.get('/history', {
        page: this.page,
        page_size: this.pageSize
      }).then(res => {
        // 添加新数据
        if (this.page === 1) {
          this.historyList = res.list || [];
        } else {
          this.historyList = [...this.historyList, ...(res.list || [])];
        }
        
        // 更新总数和是否有更多
        this.totalCount = res.total || 0;
        this.hasMore = this.historyList.length < this.totalCount;
        
        // 页码加1
        this.page++;
      }).catch(err => {
        uni.showToast({
          title: '获取历史记录失败',
          icon: 'none'
        });
      }).finally(() => {
        this.isLoading = false;
      });
    },
    
    // 加载更多历史记录
    loadMoreHistory() {
      if (this.hasMore) {
        this.loadHistoryList();
      }
    },
    
    // 查看历史记录详情
    viewHistoryDetail(recordId) {
      uni.navigateTo({
        url: `/pages/chat/chat?recordId=${recordId}`
      });
    },
    
    // 确认删除
    confirmDelete(recordId) {
      uni.showModal({
        title: '确认删除',
        content: '确定删除这条历史记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.deleteHistory(recordId);
          }
        }
      });
    },
    
    // 删除历史记录
    deleteHistory(recordId) {
      uni.showLoading({
        title: '删除中...'
      });
      
      // 调用API删除历史记录
      request.delete(`/history/${recordId}`).then(res => {
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        });
        
        // 从列表中移除
        this.historyList = this.historyList.filter(item => item.id !== recordId);
      }).catch(err => {
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        });
      }).finally(() => {
        uni.hideLoading();
      });
    },
    
    navigateToChat() {
      uni.navigateTo({
        url: '/pages/chat/chat'
      });
    },
    
    navigateToHistory() {
      // 已经在历史记录页面，不需要跳转
    }
  }
}
</script>

<style>
.history-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f9f9f9;
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

.history-list {
  margin-top: calc(43px + 90rpx); /* 系统状态栏 + 导航栏高度 */
  margin-bottom: 120rpx;
  flex: 1;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  padding: 30rpx;
  margin-bottom: 2rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.history-content {
  flex: 1;
}

.history-title {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 10rpx;
  display: block;
}

.history-time {
  font-size: 24rpx;
  color: #999;
}

.history-actions {
  display: flex;
  align-items: center;
}

.history-delete {
  color: #999;
  font-size: 40rpx;
  margin-right: 20rpx;
  padding: 10rpx;
}

.history-arrow {
  color: #ccc;
  font-size: 40rpx;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 100rpx 0;
}

.loading-more {
  text-align: center;
  color: #999;
  padding: 20rpx 0;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background-color: white;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
  height: 120rpx;
  padding-bottom: 35rpx;
}

.nav-btn {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #666;
}

.nav-btn.active {
  color: #1565C0;
  font-weight: bold;
}

.nav-text {
  font-size: 30rpx;
}
</style>
