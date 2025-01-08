<template>
    <table class="table">
        <thead>
            <tr>
                <th v-for="(header, index) in headers" :key="index" class="table_head" scope="col">{{ header }}</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(row, rowIndex, index) in tableData" :key="rowIndex">
                <td class="text-align-center vertical-align-middle"> {{ row.version }} </td>
                <td class="vertical-align-middle">{{ row.id }}</td>

                <td class="vertical-align-middle">{{ row.username }}</td>
                <td class="vertical-align-middle">{{ row.user_group }}</td>
                <td class="vertical-align-middle">{{ row.operation_description }}</td>
                <td class="vertical-align-middle">{{ row.update_description }}</td>
                <td class="vertical-align-middle">{{ row.timestamp }}</td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
import {
    computed,
    defineComponent
} from 'vue'
import { useStore } from '@/stores/store';
const store = useStore()

const props = defineProps(['headers', 'rows', 'tableData'])

</script>

<style scoped>
thead {
    th {

        border-bottom: 2px solid black !important;
        font-weight: 500;
        background-color: #5632d0;
        color: #fff;
        text-transform: capitalize
    }
}

td {
    border: 1px solid grey
}

th,
td {
    padding: .5rem
}

.text-align-center {
    text-align: center;
}

.vertical-align-middle {
    vertical-align: middle;
}
</style>