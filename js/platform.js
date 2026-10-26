/**
 * UNIVERSAL GLOBAL PLATFORM SDK BRIDGE (v2.0.0)
 * Optimized for Western & Global Web Game Portals & Messengers:
 * - Poki (Poki SDK v2)
 * - CrazyGames (CrazyGames SDK v2/v3)
 * - Telegram Mini Apps (Global TMA + Haptic + CloudStorage + Adsgram)
 * - GameDistribution / Azerion (GD SDK)
 * - Facebook Instant Games (FBInstant SDK)
 * - Standalone Web / Mobile Safari & Chrome / Localhost Dev
 */

(function(window) {
  'use strict';

  const Platform = {
    type: 'web', // 'poki' | 'crazygames' | 'telegram' | 'gamedistribution' | 'fbinstant' | 'web'
    isReady: false,
    lastInterstitialTime: 0,
    interstitialCooldown: 60000, // 60s cooldown between mid-roll ads

    /**
     * Platform detection and SDK initialization
     */
    async init() {
      console.log('[Platform] Initializing Global SDK Bridge...');

      // 1. Poki SDK
      if (typeof window.PokiSDK !== 'undefined') {
        this.type = 'poki';
        try {
          await window.PokiSDK.init();
          console.log('[Platform] Poki SDK initialized successfully');
        } catch (e) {
          console.warn('[Platform] PokiSDK.init warning:', e);
        }
      }
      // 2. CrazyGames SDK
      else if (window.CrazyGames && window.CrazyGames.SDK) {
        this.type = 'crazygames';
        try {
          if (typeof window.CrazyGames.SDK.init === 'function') {
            await window.CrazyGames.SDK.init();
          }
          console.log('[Platform] CrazyGames SDK initialized successfully');
        } catch (e) {
          console.warn('[Platform] CrazyGames SDK init warning:', e);
        }
      }
      // 3. Telegram Mini Apps (Global TMA)
      else if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData) {
        this.type = 'telegram';
        try {
          window.Telegram.WebApp.ready();
          window.Telegram.WebApp.expand();
          if (typeof window.Telegram.WebApp.disableVerticalSwipes === 'function') {
            window.Telegram.WebApp.disableVerticalSwipes();
          }
          console.log('[Platform] Running inside Telegram Mini App');
        } catch (e) {
          console.warn('[Platform] Telegram WebApp setup error:', e);
        }
      }
      // 4. Facebook Instant Games
      else if (typeof window.FBInstant !== 'undefined') {
        this.type = 'fbinstant';
        try {
          await window.FBInstant.initializeAsync();
          console.log('[Platform] Facebook Instant Games SDK initialized');
        } catch (e) {
          console.warn('[Platform] FBInstant initialize error:', e);
        }
      }
      // 5. GameDistribution (Azerion)
      else if (typeof window.gdsdk !== 'undefined' || typeof window.gdApi !== 'undefined' || typeof window.GameDistribution !== 'undefined') {
        this.type = 'gamedistribution';
        console.log('[Platform] GameDistribution SDK detected');
      }
      // 6. Standalone Web / Mobile Browser / Localhost
      else {
        this.type = 'web';
        console.log('[Platform] Running in Standalone Web / Dev Mode');
      }

      this.isReady = true;
      this._setupAudioUnlock();
      this._setupVisibilityLifecycle();

      return this.type;
    },

    /**
     * Signal to platform that loading is finished and game is ready for interaction
     */
    gameReady() {
      console.log(`[Platform] gameReady() called on [${this.type}]`);

      // Poki: Game loading finished
      if (this.type === 'poki' && window.PokiSDK) {
        try {
          window.PokiSDK.gameLoadingFinished();
        } catch (e) {}
      }

      // Facebook Instant Games: Start game
      if (this.type === 'fbinstant' && window.FBInstant) {
        try {
          window.FBInstant.startGameAsync();
        } catch (e) {}
      }
    },

    /**
     * Signal that active combat/gameplay has started (unpaused action)
     */
    gameplayStart() {
      console.log('[Platform] gameplayStart()');
      if (this.type === 'poki' && window.PokiSDK) {
        window.PokiSDK.gameplayStart();
      }
      if (this.type === 'crazygames' && window.CrazyGames?.SDK?.game) {
        window.CrazyGames.SDK.game.gameplayStart();
      }
    },

    /**
     * Signal that active combat/gameplay has stopped (menu, pause, game over)
     */
    gameplayStop() {
      console.log('[Platform] gameplayStop()');
      if (this.type === 'poki' && window.PokiSDK) {
        window.PokiSDK.gameplayStop();
      }
      if (this.type === 'crazygames' && window.CrazyGames?.SDK?.game) {
        window.CrazyGames.SDK.game.gameplayStop();
      }
    },

    /**
     * Trigger a "Happy Time" celebration event (CrazyGames milestone celebration)
     */
    happytime() {
      if (this.type === 'crazygames' && window.CrazyGames?.SDK?.game) {
        try {
          window.CrazyGames.SDK.game.happytime();
        } catch (e) {}
      }
    },

    /**
     * Show a rewarded video ad
     * @param {function(boolean)} callback(isRewarded)
     */
    rewarded(callback) {
      if (typeof callback !== 'function') callback = () => {};
      console.log(`[Platform] Requesting Rewarded Ad on [${this.type}]`);

      const prevVolume = (window.Sfx && typeof window.Sfx.volume === 'number') ? window.Sfx.volume : 0.85;
      const muteGame = () => { if (window.Sfx) window.Sfx.setVolume(0); };
      const unmuteGame = () => { if (window.Sfx) window.Sfx.setVolume(prevVolume); };

      // 1. Poki
      if (this.type === 'poki' && window.PokiSDK) {
        muteGame();
        window.PokiSDK.rewardedBreak()
          .then((success) => {
            unmuteGame();
            callback(success);
          })
          .catch(() => {
            unmuteGame();
            callback(false);
          });
        return;
      }

      // 2. CrazyGames
      if (this.type === 'crazygames' && window.CrazyGames?.SDK?.ad) {
        muteGame();
        window.CrazyGames.SDK.ad.requestAd('rewarded', {
          adFinished: () => {
            unmuteGame();
            callback(true);
          },
          adError: (err) => {
            console.warn('[Platform] CrazyGames rewarded ad error:', err);
            unmuteGame();
            callback(false);
          }
        });
        return;
      }

      // 3. Telegram Mini Apps (via Adsgram or partner network)
      if (this.type === 'telegram' && window.Adsgram) {
        muteGame();
        try {
          const blockId = window.ADSGRAM_BLOCK_ID || "int-0";
          const AdController = window.Adsgram.init({ blockId: blockId });
          AdController.show()
            .then(() => {
              unmuteGame();
              callback(true);
            })
            .catch((err) => {
              console.warn('[Platform] Adsgram rewarded error:', err);
              unmuteGame();
              callback(false);
            });
          return;
        } catch (e) {
          unmuteGame();
        }
      }

      // 4. GameDistribution
      if (this.type === 'gamedistribution' && typeof window.gdsdk !== 'undefined' && window.gdsdk.showAd) {
        muteGame();
        window.gdsdk.showAd('rewarded')
          .then(() => {
            unmuteGame();
            callback(true);
          })
          .catch(() => {
            unmuteGame();
            callback(false);
          });
        return;
      }

      // 5. Facebook Instant Games
      if (this.type === 'fbinstant' && window.FBInstant) {
        muteGame();
        const placementId = window.FB_REWARDED_PLACEMENT_ID || 'YOUR_PLACEMENT_ID';
        window.FBInstant.getRewardedVideoAsync(placementId)
          .then(rewardedVideo => rewardedVideo.loadAsync().then(() => rewardedVideo.showAsync()))
          .then(() => {
            unmuteGame();
            callback(true);
          })
          .catch((err) => {
            console.warn('[Platform] FBInstant Rewarded error:', err);
            unmuteGame();
            callback(false);
          });
        return;
      }

      // 6. Standalone Web / Dev Mode Fallback
      console.log('[Platform] Dev Mode: Rewarded granted without real ad');
      callback(true);
    },

    /**
     * Show an interstitial / commercial break ad
     * @param {function()} callback
     */
    interstitial(callback) {
      if (typeof callback !== 'function') callback = () => {};

      const now = Date.now();
      if (now - this.lastInterstitialTime < this.interstitialCooldown) {
        console.log('[Platform] Interstitial skipped (cooldown active)');
        callback();
        return;
      }
      this.lastInterstitialTime = now;

      const prevVolume = (window.Sfx && typeof window.Sfx.volume === 'number') ? window.Sfx.volume : 0.85;
      const muteGame = () => { if (window.Sfx) window.Sfx.setVolume(0); };
      const unmuteGame = () => { if (window.Sfx) window.Sfx.setVolume(prevVolume); };

      // 1. Poki
      if (this.type === 'poki' && window.PokiSDK) {
        muteGame();
        window.PokiSDK.commercialBreak()
          .then(() => {
            unmuteGame();
            callback();
          })
          .catch(() => {
            unmuteGame();
            callback();
          });
        return;
      }

      // 2. CrazyGames
      if (this.type === 'crazygames' && window.CrazyGames?.SDK?.ad) {
        muteGame();
        window.CrazyGames.SDK.ad.requestAd('midgame', {
          adFinished: () => {
            unmuteGame();
            callback();
          },
          adError: (err) => {
            console.warn('[Platform] CrazyGames interstitial ad error:', err);
            unmuteGame();
            callback();
          }
        });
        return;
      }

      // 3. GameDistribution
      if (this.type === 'gamedistribution' && typeof window.gdsdk !== 'undefined' && window.gdsdk.showAd) {
        muteGame();
        window.gdsdk.showAd()
          .then(() => { unmuteGame(); callback(); })
          .catch(() => { unmuteGame(); callback(); });
        return;
      }

      // 4. Facebook Instant Games
      if (this.type === 'fbinstant' && window.FBInstant) {
        muteGame();
        const placementId = window.FB_INTERSTITIAL_PLACEMENT_ID || 'YOUR_PLACEMENT_ID';
        window.FBInstant.getInterstitialAdAsync(placementId)
          .then(interstitial => interstitial.loadAsync().then(() => interstitial.showAsync()))
          .then(() => { unmuteGame(); callback(); })
          .catch((err) => {
            console.warn('[Platform] FBInstant Interstitial error:', err);
            unmuteGame();
            callback();
          });
        return;
      }

      // Standalone Fallback
      callback();
    },

    /**
     * Save data to local cache and platform cloud storage
     * @param {object} data
     */
    async saveData(data) {
      if (!data) return;
      try {
        localStorage.setItem('surv_save', JSON.stringify(data));
      } catch (e) {
        // Safe catch for restrictive Safari private / incognito modes
      }

      // Telegram CloudStorage
      if (this.type === 'telegram' && window.Telegram?.WebApp?.CloudStorage) {
        try {
          window.Telegram.WebApp.CloudStorage.setItem('surv_save', JSON.stringify(data));
        } catch (e) {}
      }

      // Facebook Instant Games Cloud Data
      if (this.type === 'fbinstant' && window.FBInstant?.player) {
        try {
          await window.FBInstant.player.setDataAsync({ surv_save: data });
        } catch (e) {}
      }
    },

    /**
     * Load data from platform cloud or localStorage
     * @returns {Promise<object|null>}
     */
    async loadData() {
      // Telegram CloudStorage
      if (this.type === 'telegram' && window.Telegram?.WebApp?.CloudStorage) {
        try {
          const val = await new Promise(res => {
            window.Telegram.WebApp.CloudStorage.getItem('surv_save', (err, result) => {
              if (!err && result) res(result);
              else res(null);
            });
          });
          if (val) return JSON.parse(val);
        } catch (e) {}
      }

      // Facebook Instant Games Cloud Data
      if (this.type === 'fbinstant' && window.FBInstant?.player) {
        try {
          const cloudData = await window.FBInstant.player.getDataAsync(['surv_save']);
          if (cloudData && cloudData.surv_save) {
            return cloudData.surv_save;
          }
        } catch (e) {}
      }

      // Fallback to localStorage
      try {
        const local = localStorage.getItem('surv_save');
        if (local) return JSON.parse(local);
      } catch (e) {}

      return null;
    },

    /**
     * Mobile Haptic Feedback (Telegram & W3C Vibration API)
     * @param {'light'|'medium'|'heavy'|'success'|'warning'|'error'} style
     */
    haptic(style = 'light') {
      // Telegram Mini Apps
      if (this.type === 'telegram' && window.Telegram?.WebApp?.HapticFeedback) {
        try {
          if (style === 'success' || style === 'warning' || style === 'error') {
            window.Telegram.WebApp.HapticFeedback.notificationOccurred(style);
          } else {
            window.Telegram.WebApp.HapticFeedback.impactOccurred(style);
          }
          return;
        } catch (e) {}
      }

      // Standard W3C Vibration API (Android Chrome & modern mobile browsers)
      if (typeof navigator !== 'undefined' && navigator.vibrate) {
        try {
          const durations = {
            light: 12,
            medium: 24,
            heavy: 40,
            success: [15, 60, 20],
            warning: [25, 40, 25],
            error: [40, 60, 40]
          };
          navigator.vibrate(durations[style] || 15);
        } catch (e) {}
      }
    },

    /**
     * AudioContext unlock on iOS / mobile Safari on first user gesture
     * @private
     */
    _setupAudioUnlock() {
      const unlock = () => {
        if (window.Sfx && window.Sfx.ctx && window.Sfx.ctx.state === 'suspended') {
          window.Sfx.ctx.resume().then(() => {
            console.log('[Platform] AudioContext unlocked successfully');
          });
        }
      };
      window.addEventListener('pointerdown', unlock, { passive: true });
      window.addEventListener('touchstart', unlock, { passive: true });
      window.addEventListener('keydown', unlock, { passive: true });
    },

    /**
     * Auto-pause battle and mute audio when page/tab visibility changes
     * @private
     */
    _setupVisibilityLifecycle() {
      const onHide = () => {
        // Tab hidden or app minimized: suspend audio
        if (window.Sfx && window.Sfx.ctx && window.Sfx.ctx.state === 'running') {
          window.Sfx.ctx.suspend().catch(() => {});
        }
        // If in active battle: trigger pause modal
        if (typeof window.G !== 'undefined' && window.G && window.G.run && !window.G.pause) {
          window.G.pause = true;
          if (typeof window.openModal === 'function') {
            window.openModal('modal-pause');
          }
        }
      };

      const onShow = () => {
        // Tab restored: resume audio
        if (window.Sfx && window.Sfx.ctx && window.Sfx.ctx.state === 'suspended') {
          window.Sfx.ctx.resume().catch(() => {});
        }
      };

      document.addEventListener('visibilitychange', () => {
        if (document.hidden) onHide();
        else onShow();
      });
      window.addEventListener('pagehide', onHide);
      window.addEventListener('blur', () => {
        if (document.hidden) onHide();
      });
      window.addEventListener('pageshow', onShow);
      window.addEventListener('focus', onShow);
    }
  };

  // Export to global scope
  window.Platform = Platform;

  // Auto-init on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Platform.init());
  } else {
    Platform.init();
  }

})(window);
