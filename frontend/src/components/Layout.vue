<template>
    <div>
        <Navbar />
        <main class="main">
            <slot></slot>
        </main>
        <Footer />
    </div>
</template>
<script>
import Navbar from './Navbar.vue'
import Footer from './Footer.vue';

export default {
    name: 'Layout',
    setup() {

    },
    components: {
        Navbar,
        Footer
    }
}
</script>

<style>
.main {
    background-color: #F8F9FA;
    margin-bottom: 5rem;
}
</style>