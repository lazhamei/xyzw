import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/index';

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null);
  const token = ref(localStorage.getItem('token') || null);
  const isLoading = ref(false);

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userInfo = computed(() => user.value);

  // 登录
  const login = async (credentials) => {
    try {
      isLoading.value = true;
      const response = await api.auth.login(credentials);

      if (response.success) {
        token.value = response.data.token;
        if (response.data.user) {
          user.value = response.data.user;
        }

        // 保存到本地存储
        localStorage.setItem('token', token.value);
        if (user.value) {
          localStorage.setItem('user', JSON.stringify(user.value));
        }

        return { success: true };
      } else {
        return { success: false, message: response.message || '登录失败' };
      }
    } catch (error) {
      console.error('登录错误:', error);
      return {
        success: false,
        message: error.response?.data?.message || '登录失败',
      };
    } finally {
      isLoading.value = false;
    }
  };

  // 注册
  const register = async (userInfo) => {
    try {
      isLoading.value = true;
      const response = await api.auth.register(userInfo);

      if (response.success) {
        if (response.data.token) {
          token.value = response.data.token;
          localStorage.setItem('token', token.value);
        }
        return { success: true, message: response.message || '注册成功' };
      } else {
        return { success: false, message: response.message || '注册失败' };
      }
    } catch (error) {
      console.error('注册错误:', error);
      return {
        success: false,
        message: error.response?.data?.message || '注册失败',
      };
    } finally {
      isLoading.value = false;
    }
  };

  // 登出
  const logout = () => {
    user.value = null;
    token.value = null;

    // 清除本地存储
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      if (!token.value) return false;

      const response = await api.auth.getUserInfo();
      if (response.success) {
        user.value = response.data;
        localStorage.setItem('user', JSON.stringify(user.value));
        return true;
      } else {
        logout();
        return false;
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
      logout();
      return false;
    }
  };

  // 刷新token
  const refreshToken = async () => {
    try {
      const response = await api.auth.refreshToken();
      if (response.success) {
        token.value = response.data.token;
        localStorage.setItem('token', token.value);
        return true;
      }
      return false;
    } catch (error) {
      console.error('刷新token失败:', error);
      return false;
    }
  };

  // 初始化认证状态
  const initAuth = async () => {
    if (token.value) {
      try {
        await fetchUserInfo();
      } catch (error) {
        console.error('初始化认证失败:', error);
        logout();
      }
    }
  };

  return {
    // 状态
    user,
    token,
    isLoading,

    // 计算属性
    isAuthenticated,
    userInfo,

    // 方法
    login,
    register,
    logout,
    fetchUserInfo,
    refreshToken,
    initAuth,
  };
});
