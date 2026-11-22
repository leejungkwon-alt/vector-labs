import { useAuthStore } from './authStore';
import { api, setAuthToken } from '../api/client';
import { storage } from './secureStore';

// Mock `api` client
jest.mock('../api/client', () => ({
  api: {
    anonymous: jest.fn(() => Promise.resolve({ access_token: 'new_anonymous_token', user: { id: 'anon_user', is_anonymous: true } })),
    me: jest.fn(() => Promise.resolve({ user: { id: 'guest_user', is_anonymous: false } })),
  },
  setAuthToken: jest.fn(),
}));

// Mock `secureStore`
jest.mock('./secureStore', () => ({
  storage: {
    getItem: jest.fn((key) => {
      if (key === 'saju.access_token') return Promise.resolve('test_token');
      if (key === 'saju.guest_token_backup') return Promise.resolve('guest_backup_token');
      return Promise.resolve(null);
    }),
    setItem: jest.fn(() => Promise.resolve()),
    deleteItem: jest.fn(() => Promise.resolve()),
  },
}));

describe('authStore', () => {
  beforeEach(() => {
    // Reset Zustand store state before each test
    useAuthStore.setState({ user: null, ready: false, authError: null });
    jest.clearAllMocks();
  });

  it('should set initial state correctly', () => {
    const user = useAuthStore.getState().user;
    expect(user).toBeNull();
  });

  describe('signOut', () => {
    it('should clear the user and token, then re-issue an anonymous token if no guest backup', async () => {
      // Set an initial authenticated user
      useAuthStore.setState({ user: { id: 'test_user', tier: 'free', is_anonymous: false, social_provider: null, social_subject: null, created_at: '2023-01-01T00:00:00Z', onetime_credits: 0 }, ready: true });
      // Make sure there's no guest backup token
      (storage.getItem as jest.Mock).mockImplementation((key: string) => {
        if (key === 'saju.access_token') return Promise.resolve('test_token');
        return Promise.resolve(null); // No guest backup
      });

      await useAuthStore.getState().signOut();

      expect(setAuthToken).toHaveBeenCalledWith(null); // Token cleared
      expect(useAuthStore.getState().user).toEqual({ id: 'anon_user', is_anonymous: true }); // New anonymous user
      expect(storage.deleteItem).toHaveBeenCalledWith('saju.access_token'); // Original token deleted
      expect(api.anonymous).toHaveBeenCalledTimes(1); // Anonymous token re-issued
      expect(storage.setItem).toHaveBeenCalledWith('saju.access_token', 'new_anonymous_token'); // New token saved
    });

    it('should restore guest token if available after signOut', async () => {
      // Set an initial authenticated user
      useAuthStore.setState({ user: { id: 'logged_in_user', tier: 'free', is_anonymous: false, social_provider: null, social_subject: null, created_at: '2023-01-01T00:00:00Z', onetime_credits: 0 }, ready: true });
      // Ensure guest backup token exists
      (storage.getItem as jest.Mock).mockImplementation((key: string) => {
        if (key === 'saju.access_token') return Promise.resolve('initial_token');
        if (key === 'saju.guest_token_backup') return Promise.resolve('guest_backup_token_to_restore');
        return Promise.resolve(null);
      });
      // Mock api.me to return a user for the restored guest token
      (api.me as jest.Mock).mockResolvedValueOnce({ user: { id: 'restored_guest', tier: 'free', is_anonymous: true, social_provider: null, social_subject: null, created_at: '2023-01-01T00:00:00Z', onetime_credits: 0 } });

      await useAuthStore.getState().signOut();

      expect(setAuthToken).toHaveBeenCalledWith(null); // Original token cleared first
      expect(setAuthToken).toHaveBeenCalledWith('guest_backup_token_to_restore'); // Guest token restored
      expect(useAuthStore.getState().user).toEqual({ id: 'restored_guest', is_anonymous: true, tier: 'free', social_provider: null, social_subject: null, created_at: '2023-01-01T00:00:00Z', onetime_credits: 0 }); // User updated to restored guest
      expect(storage.deleteItem).not.toHaveBeenCalledWith('saju.access_token'); // Original token is NOT deleted if guest backup is restored
      expect(storage.deleteItem).toHaveBeenCalledWith('saju.guest_token_backup'); // Backup token cleared after restore
      expect(api.me).toHaveBeenCalledTimes(1); // `api.me` called to get user for guest token
      expect(api.anonymous).not.toHaveBeenCalled(); // No anonymous re-issue if guest restored
      expect(storage.setItem).toHaveBeenCalledWith('saju.access_token', 'guest_backup_token_to_restore'); // Restored token saved as current
    });
  });

  describe('signInAnonymous', () => {
    it('should create an anonymous user and set the token', async () => {
      // Mock api.anonymous to return a full user object
      (api.anonymous as jest.Mock).mockResolvedValueOnce({ 
        access_token: 'new_anonymous_token', 
        user: { id: 'anon_user', tier: 'free', is_anonymous: true, social_provider: null, social_subject: null, created_at: '2023-01-01T00:00:00Z', onetime_credits: 0 }
      });
      await useAuthStore.getState().signInAnonymous();

      expect(api.anonymous).toHaveBeenCalledTimes(1);
      expect(setAuthToken).toHaveBeenCalledWith('new_anonymous_token');
      expect(storage.setItem).toHaveBeenCalledWith('saju.access_token', 'new_anonymous_token');
      expect(useAuthStore.getState().user).toEqual({ id: 'anon_user', is_anonymous: true, tier: 'free', social_provider: null, social_subject: null, created_at: '2023-01-01T00:00:00Z', onetime_credits: 0 });
      expect(useAuthStore.getState().ready).toBe(false); // signInAnonymous does not set ready to true
    });
  });
});
