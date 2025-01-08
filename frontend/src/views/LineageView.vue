<template>
    <Layout>
        <div class="container bg-body-tertiary">
            <div class="row">
                <h3 class="py-4">Lineage Tracker</h3>
                <div class="display-state-btn-container">
                    <button :class="`display-state-btn tracker-btn ${store.displayState === 'tracker' ? 'active' : ''}`"
                        @click="setDisplayState('tracker')">Data tables</button>
                    <button :class="`display-state-btn diff-btn ${store.displayState === 'diff' ? 'active' : ''}`"
                        @click="setDisplayState('diff')">Compare lineages</button>
                </div>
                <div class="col-4">
                    <div>
                        <TreeComponent v-if="store.treeObject" :addToDiff="store.addtoDiff"
                            :selectedDiff="store.selectedDiff" :data="store.treeObject" />
                    </div>
                </div>
                <div class="col-8 diff-display-content">
                    <div v-if="store.displayState === 'diff'">
                        <div v-if="store.selectedDiff.length < 1">
                            <div class="">
                                <p>Please click and select two tree nodes to compare datasets</p>
                            </div>
                        </div>
                        <div v-else-if="store.selectedDiff.length === 1">
                            <div>
                                <p>Please select one more tree node to compare datasets</p>
                            </div>

                        </div>
                        <div v-else>
                            <CompareView />
                        </div>

                    </div>
                    <div v-else>
                        <Table
                            :headers="['Version', 'UUID', 'User', 'User Group', 'Activity', 'Activity Description', 'Timestamp']"
                            :tableData="store.tableData" :rows="store.getDatasetHistory()" />
                    </div>
                </div>
            </div>
        </div>
        <Compare />
    </Layout>
</template>

<script setup>
import {
    useStore
} from '../stores/store'
import Layout from '../components/Layout.vue'

import Table from '../components/Table.vue'
import CompareView from '../components/compare/CompareView.vue'

import TreeComponent from '../components/TreeComponent.vue';
import { useRoute } from 'vue-router'

const route = useRoute()

const lineageID = route.params.id


const store = useStore()
store.fetchData(lineageID)


const setDisplayState = (viewState) => {
    store.displayState = viewState
}

</script>

<style>
.headline {
    color: #613deb;
    font-family: 'Poppins', sans-serif;
}


.tree {
    width: 100%;
    text-align: center;
}

.tree ul {
    padding-top: 20px;
    position: relative;
    transition: .5s;
}

.tree li {
    display: inline-table;
    text-align: center;
    list-style-type: none;
    position: relative;
    padding: 10px;
    transition: .5s;
}

.tree li::before,
.tree li::after {
    content: '';
    position: absolute;
    top: 0;
    right: 50%;
    border-top: 1px solid #ccc;
    width: 51%;
    height: 10px;
}

.tree li::after {
    right: auto;
    left: 50%;
    border-left: 1px solid #ccc;
}

.tree li:only-child::after,
.tree li:only-child::before {
    display: none;
}

.tree li:only-child {
    padding-top: 0;
}

.tree li:first-child::before,
.tree li:last-child::after {
    border: 0 none;
}

.tree li:last-child::before {
    border-right: 1px solid #ccc;
    border-radius: 0 5px 0 0;
}

.tree li:first-child::after {
    border-radius: 5px 0 0 0;
}

.tree ul ul::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    border-left: 1px solid #ccc;
    width: 0;
    height: 20px;
}

.tree li a {
    border: 1px solid #ccc;
    padding: 15px;
    display: inline-block;
    /* border-radius: 5px; */
    text-decoration-line: none;
    transition: .5s;
}

.tree li a img {
    width: 50px;
    height: 50px;
    border-radius: 100px;
    margin-bottom: 10px;
}

.tree li a span {
    border: 1px solid #ccc;
    border-radius: 20px;
    color: #666;
    padding: 8px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}

.diff-display-content {
    display: flex;
    justify-content: center;
}

.display-state-btn-container {
    display: flex;

    .tracker-btn {
        border-top-right-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
        border-right: none !important;
    }

    .diff-btn {
        border-top-left-radius: 0 !important;
        border-bottom-left-radius: 0 !important;
        border-left: none !important;
    }

    .display-state-btn {
        font-weight: 500;
        color: #52525b;
        border: 1.4px solid #e4e4e7;
        outline: none;
        border-radius: .375rem;
        padding: .5rem .75rem !important;

        &.active {
            background-color: #462ba8;
            color: #fff;

        }
    }
}
</style>
