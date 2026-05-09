import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/index';

export const useTokenStore = defineStore('tokens', () => {
  const gameTokens = ref<any[]>([]);
  const selectedTokenId = ref<string | null>(null);
  const isLoading = ref(false);

  const hasTokens = computed(() => gameTokens.value.length > 0);

  const selectedToken = computed(() => {
    return gameTokens.value.find((t) => t.id === selectedTokenId.value);
  });

  async function fetchTokens() {
    try {
      isLoading.value = true;
      const response = await api.gameRoles.getList();
      if (response.success) {
        gameTokens.value = response.data || [];
      }
    } catch (error) {
      console.error('[TokenStore] Fetch tokens error:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function addToken(tokenData: any) {
    try {
      isLoading.value = true;
      const response = await api.gameRoles.add(tokenData);
      if (response.success) {
        gameTokens.value.push(response.data);
        return response.data;
      }
    } catch (error) {
      console.error('[TokenStore] Add token error:', error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateToken(tokenId: string, updates: any) {
    try {
      isLoading.value = true;
      const response = await api.gameRoles.update(tokenId, updates);
      if (response.success) {
        const index = gameTokens.value.findIndex((t) => t.id === tokenId);
        if (index !== -1) {
          gameTokens.value[index] = { ...gameTokens.value[index], ...response.data };
        }
        return true;
      }
    } catch (error) {
      console.error('[TokenStore] Update token error:', error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteToken(tokenId: string) {
    try {
      isLoading.value = true;
      const response = await api.gameRoles.delete(tokenId);
      if (response.success) {
        gameTokens.value = gameTokens.value.filter((t) => t.id !== tokenId);
        if (selectedTokenId.value === tokenId) {
          selectedTokenId.value = null;
        }
        return true;
      }
    } catch (error) {
      console.error('[TokenStore] Delete token error:', error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  function selectToken(tokenId: string) {
    selectedTokenId.value = tokenId;
  }

  return {
    gameTokens,
    selectedTokenId,
    isLoading,
    hasTokens,
    selectedToken,
    fetchTokens,
    addToken,
    updateToken,
    deleteToken,
    selectToken,
  };
});
