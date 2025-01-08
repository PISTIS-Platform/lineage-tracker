import Keycloak from 'keycloak-js'
import config from '@/config/config'

const options = {
  url: config.keycloak.url,
  clientId: config.keycloak.clientId,
  realm: config.keycloak.realm
  // secret: import.meta.env.VITE_KEYCLOAK_CLIENT_SECRET
}

const keycloak = new Keycloak(options)
let authenticated
let store = null

/**
 * Initializes Keycloak, then run callback. This will prompt you to login.
 *
 * @param onAuthenticatedCallback
 */
async function init(onInitCallback) {
  try {
    authenticated = await keycloak.init({ onLoad: 'login-required' })
    onInitCallback()
  } catch (error) {
    console.error('Keycloak init failed')
    console.error(error)
  }
}

/**
 * Initializes store with Keycloak user data
 *
 */
async function initStore(storeInstance) {
  try {
    store = storeInstance
    store.initOauth(keycloak)

    // Show alert if user is not authenticated
    if (!authenticated) {
      alert('not authenticated')
    }
  } catch (error) {
    console.error('Keycloak init failed')
    console.error(error)
  }
}

/**
 * Logout user
 */
function logout(url) {
  keycloak.logout({ redirectUri: url })
}

/**
 * Refreshes token
 */
async function refreshToken() {
  try {
    await keycloak.updateToken(480)
    return keycloak
  } catch (error) {
    console.error('Failed to refresh token')
    console.error(error)
  }
}

const KeycloakService = {
  CallInit: init,
  CallInitStore: initStore,
  CallLogout: logout,
  CallTokenRefresh: refreshToken
}

export default KeycloakService
