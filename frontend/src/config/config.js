// config js
export default {
    navigation : [
        { name: 'Home', icon: 'house' },
        { name: 'My Data', icon: 'database' },
        { name: 'My Transactions', icon: 'arrow-right-arrow-left' },
        { name: 'Pistis Market', icon: 'store' },
        { name: 'Manage Services', icon: 'clipboard-list' },
        { name: 'Resources and activities monitor', icon: 'chart-line' }
    ],
    subNav: [
        { name: 'Wallet' },
        { name: 'Data Log' },
        { name: 'Models Manager' },
        { name: 'Purchase/Subscription Plan Designer' },
        { name: 'Data Usage and Intensions Analytics' },
    ],
    keycloak: {
        realm: 'PISTIS',
        clientId: 'fhg-ui-test',
        url: 'https://auth.pistis-market.eu/auth',
        loginUrl: 'https://pistis-market.eu/',
        logoutUrl: 'https://develop.pistis-market.eu/'
    }
}
