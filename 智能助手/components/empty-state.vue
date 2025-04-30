<template>
  <view class="empty-container">
    <image class="empty-image" :src="image" mode="aspectFit"></image>
    <text class="empty-text">{{ text }}</text>
    <view v-if="buttonText" class="empty-button" @click="$emit('buttonClick')">
      {{ buttonText }}
    </view>
  </view>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    // 显示的图片
    image: {
      type: String,
      default: '/static/images/empty.png'
    },
    // 显示的文字
    text: {
      type: String,
      default: '暂无数据'
    },
    // 按钮文字，不传则不显示按钮
    buttonText: {
      type: String,
      default: ''
    }
  }
}
</script>

<style>
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx;
}

.empty-image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 30rpx;
}

.empty-button {
  font-size: 28rpx;
  color: #1565C0;
  padding: 15rpx 30rpx;
  border: 1rpx solid #1565C0;
  border-radius: 30rpx;
}
</style>
