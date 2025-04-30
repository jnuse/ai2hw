<script>
import storage from './utils/storage';
import config from './config';

export default {
  onLaunch: function() {
    console.log('App Launch');
    // 检查登录状态
    const token = uni.getStorageSync(config.TOKEN_KEY);
    if (!token) {
      uni.reLaunch({
        url: '/pages/login/login'
      });
    }
  },
  onShow: function() {
    console.log('App Show');
  },
  onHide: function() {
    console.log('App Hide');
  }
};
</script>

<style>
@import './static/style/common.css';
</style>
