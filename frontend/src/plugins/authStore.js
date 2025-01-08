import { useAuthStore } from '@/stores/authStore.js'
import keycloakService from '../services/keycloakService'

// Setup auth store as a plugin so it can be accessed globally in our FE
const authStorePlugin = {
  install(app, option) {
    const store = useAuthStore(option.pinia)

    // Global store
    app.config.globalProperties.$store = store

    // Store keycloak user data into store
    keycloakService.CallInitStore(store)
  }
}

export default authStorePlugin
