import Vue from 'vue'
import App from './App'

Vue.config.productionTip = false

// 全局混入
Vue.mixin({
  methods: {
    // 全局方法示例
    $showToast(title, icon = 'none') {
      uni.showToast({
        title,
        icon
      })
    }
  }
})

App.mpType = 'app'

const app = new Vue({
  ...App
})
app.$mount()
