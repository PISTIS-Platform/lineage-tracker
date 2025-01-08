<template>

    <div class="container bg-body-tertiary">
        <div class="row">
            <div class="col-12">
                <div class="d-flex table-container">
                    <div class="col-6">
                        <h4>Dataset version {{ store.selectedDiff?.[0] }}</h4>
                        <table border="1">
                            <thead>
                                <tr>
                                    <th v-for="(column, index) in dataset1Columns" :key="column.name"
                                        :class="getColumnClass(column.name, 1)">
                                        {{ column.name }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(row, rowIndex) in dataset1Data" :key="rowIndex">
                                    <td v-for="(value, index) in row" :key="index"
                                        :class="getClass(value, index, rowIndex, 1)">
                                        {{ value }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="col-6">
                        <h4>Dataset version {{ store.selectedDiff?.[1] }}</h4>
                        <table border="1">
                            <thead>
                                <tr>
                                    <th v-for="(column, index) in dataset2Columns" :key="column.name"
                                        :class="getColumnClass(column.name, 2)">
                                        {{ column.name }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(row, rowIndex) in dataset2Data" :key="rowIndex">
                                    <td v-for="(value, index) in row" :key="index"
                                        :class="getClass(value, index, rowIndex, 2)">
                                        {{ value }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>

                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="py-3">Legend:</div>
            <ul>
                <li>
                    <div class="rounded-circle column-added" style="width:10px; height:10px;float:left;"></div>Added
                </li>
                <li>
                    <div class="rounded-circle blue" style="width:10px; height:10px;float:left;"></div>Changed
                </li>
                <li>
                    <div class="rounded-circle green" style="width:10px; height:10px;float:left;"></div>Columns
                    added
                </li>
                <li>
                    <div class="rounded-circle pink" style="width:10px; height:10px;float:left;"></div>Columns
                    removed
                </li>
            </ul>

        </div>
    </div>
    <div>
    </div>

</template>

<script setup>
import {
 ref
} from 'vue'
import {
    useStore
} from '../../stores/store'
const store = useStore();


const diffdata = {
    "dataset_1": [
        {
            "data_model": {
                "columns": [
                    { "name": "entry_id", "dataType": "Integer" },
                    { "name": "age", "dataType": "Integer" },
                    { "name": "name", "dataType": "String" },
                    { "name": "sex", "dataType": "String" },
                    { "name": "hiring_date", "dataType": "Date" }
                ]
            },
            "data": {
                "rows": [
                    [1, 43, "Alice", "f", "2012.05.22"],
                    [2, 40, "Bob", "m", "2008.05.22"],
                    [3, 20, "Charlie", "m", "2009.04.21"]
                ]
            }
        }
    ],
    "dataset_2": [
        {
            "data_model": {
                "columns": [
                    { "name": "entry_id", "dataType": "Integer" },
                    { "name": "age", "dataType": "Integer" },
                    { "name": "name", "dataType": "String" },
                    { "name": "sex", "dataType": "String" },
                    { "name": "city", "dataType": "String" }
                ]
            },
            "data": {
                "rows": [
                    [1, 42, "Bob", "m", "Munich"],
                    [3, 20, "Charlie", "m", "Leipzig"],
                    [4, 30, "Dana", "f", "Berlin"]
                ]
            }
        }
    ],
    "diff": {
        "added": [
            { "entry_id": "4", "age": "30", "name": "Dana", "sex": "f", "hiring_date": "2009.07.21" }
        ],
        "removed": [
            { "entry_id": "2", "age": "40", "name": "Bob", "sex": "m", "hiring_date": "2008.05.22" }
        ],
        "changed": [
            {
                "key": "1",
                "changes": {
                    "age": ["43", "42"],
                    "name": ["Alice", "Bob"],
                    "sex": ["f", "m"],
                    "hiring_date": ["2012.05.22", "2008.05.22"]
                }
            }
        ],
        "columns_added": ["city"],
        "columns_removed": ["hiring_date"]
    }
};




const dataset1 = ref(diffdata.dataset_1[0]);
const dataset2 = ref(diffdata.dataset_2[0]);
const dataset1Columns = ref(dataset1.value.data_model.columns);
const dataset2Columns = ref(dataset2.value.data_model.columns);
const dataset1Data = ref(dataset1.value.data.rows);
const dataset2Data = ref(dataset2.value.data.rows);

const getClass = (value, index, rowIndex, dataset) => {
    const columnName = dataset === 1 ? dataset1Columns.value[index].name : dataset2Columns.value[index].name;
    const { added, removed, changed, columns_added, columns_removed } = diffdata.diff;

    // Check for added rows
    if (dataset === 2) {
        for (let add of added) {
            if (parseInt(add.entry_id) - 1 === rowIndex) {
                return 'added';
            }
        }
    }

    // Check for removed rows
    if (dataset === 1) {
        for (let remove of removed) {
            if (parseInt(remove.entry_id) - 1 === rowIndex) {
                return 'removed';
            }
        }
    }

    // Check for changed values
    for (let change of changed) {
        if (parseInt(change.key) - 1 === rowIndex) {
            const oldValue = change.changes[columnName] && change.changes[columnName][0];
            const newValue = change.changes[columnName] && change.changes[columnName][1];

            if (dataset === 1 && value == oldValue) return 'modified';
            if (dataset === 2 && value == newValue) return 'modified';
        }
    }

    // Check for added columns
    if (dataset === 2 && columns_added.includes(columnName)) {
        return 'column-added';
    }

    // Check for removed columns
    if (dataset === 1 && columns_removed.includes(columnName)) {
        return 'column-removed';
    }

    return '';
};

const getColumnClass = (columnName, dataset) => {
    const { columns_added, columns_removed } = diffdata.diff;

    if (dataset === 1 && columns_removed.includes(columnName)) {
        return 'column-removed';
    }

    if (dataset === 2 && columns_added.includes(columnName)) {
        return 'column-added';
    }

    return '';
};
</script>

<style scoped>
.green,
.added,
.column-added {
    /* background: #90EE90 !important; */
    background-color: red;
}

.blue,
.modified {
    background: #87CEFA !important;
}

.pink,
.removed,
.column-removed {
    background: #FFB6C1 !important;
}

table {
    width: 100%;
}

ul {
    list-style: none;
}

.column-added {
    background-color: lightgreen;
    color: black;
}

.column-removed {
    background-color: pink;
    color: black;
}


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

.table-container {
    gap: 1rem;

    h2 {
        text-align: center;
    }
}
</style>
