import { defineStore } from 'pinia'
import config from '../config/config'
import axios from 'axios'
import { ref } from 'vue'
import { useAuthStore } from '../stores/authStore'




export const useStore = defineStore('store', () => {
    const selectedOption = ref('dataset-history')
    const isCompareVisible = ref(false)
    const navigation = ref(config.navigation)
    const subNav = ref(config.subNav)
    const familyTreeData = ref(null)
    const treeObject = ref(null)

    const authStore = useAuthStore()

    const tableData = ref(null)

    //ref to store version of selected tree nodes when using the compare view
    const selectedDiff = ref([])

    const displayState = ref("tracker")

    const sampleDiffStorage = ref(
        'Array item diff 1',
    )


    //function handling storage of diff versions when tree nodes are clicked
    const addtoDiff = (diffID) => {
        selectedDiff.value.push(diffID)
        if (selectedDiff.value.length > 2) {
            selectedDiff.value = []
            addtoDiff(diffID)
            console.log(selectedDiff.value);

        } else if (selectedDiff.value.length === 2) {
            sampleDiffStorage.value = `Value 1:${selectedDiff.value?.[0]} Value 2:${selectedDiff.value?.[1]}`
            console.log(sampleDiffStorage.value);
            displayState.value = "diff"
            //api call to diff endpoint to be made directly under this comment (simple send index 0 and index 1 to diff backend)   
        }
    }

    const resetDiff = () => {
        selectedDiff.value = []
        console.log('test reset');
    }


    const openCompare = (() => {
        isCompareVisible.value = !isCompareVisible
    })


    const getTreeData = (() => {
        const treeData = {
            // "lineage_id_1": {
            //     "uuid1": {
            //         "by": "user1",
            //         "dataset_name": "dataset1",
            //         "operation_description": "create",
            //         "timestamp": "2023-02-16T09:38:59Z",
            //         "derived_from": "None"
            //     },
            //     "uuid2": {
            //         "by": "user1",
            //         "dataset_name": "dataset2",
            //         "operation_description": "update",
            //         "timestamp": "2023-02-17T09:38:59Z",
            //         "derived_from": "uuid1"
            //     }
            // },
            // "lineage_id_2": {
            //     "uuid3": {
            //         "by": "user2",
            //         "dataset_name": "dataset3",
            //         "operation_description": "update",
            //         "timestamp": "2023-02-16T09:38:59Z",
            //         "derived_from": "uuid1"
            //     }
            // }


            "144e4f89-a5c2-4fdd-87be-144e677e7933": {
                "423abc_c": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "323abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:26:25"
                },
                "523abc_c": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "423abc_c",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:26:35"
                },
                "623abc_c": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "523abc_c",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:26:40"
                },
                "723abc_c": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "623abc_c",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:26:45"
                }
            },
            "42e581bc-0315-496b-a62b-13d33e224c0a": {
                "123abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": null,
                    "operation_description": "create",
                    "timestamp": "2024-04-02 12:40:02"
                },
                "223abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "123abc",
                    "operation_description": "update",
                    "timestamp": "2024-04-02 12:40:09"
                },
                "323abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "223abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:24:26"
                },
                "423abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "323abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:24:35"
                },
                "523abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "423abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:24:40"
                },
                "623abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "523abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:24:47"
                },
                "723abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "623abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:24:52"
                },
                "823abc": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "723abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:24:57"
                }
            },
            "953a9bdb-92d8-4c4c-8f6f-92e6cc460c19": {
                "223abc_b": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "123abc",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:25:26"
                },
                "323abc_b": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "223abc_b",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:25:40"
                },
                "423abc_b": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "323abc_b",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:25:45"
                },
                "523abc_b": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "423abc_b",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:25:49"
                },
                "623abc_b": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "523abc_b",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:25:54"
                },
                "723abc_b": {
                    "by": "user1",
                    "dataset_name": "random_name",
                    "derived_from": "623abc_b",
                    "operation_description": "update",
                    "timestamp": "2024-05-23 13:25:59"
                }
            }
        }
        treeObject.value = treeData
        familyTreeData.value = treeData
    })

    // GET -> Dataset History
    const getDatasetHistory = (() => {
        // Assume data is fetched from API
        const tableData = [{
            "by": "user1",
            "operation_description": "create",
            "timestamp": "2024-04-05 14:10:21"
        },
        {
            "by": "user2",
            "operation_description": "read",
            "timestamp": "2024-04-05 14:10:23"
        },
        {
            "by": "user1",
            "operation_description": "delete",
            "timestamp": "2024-04-05 14:10:24"
        }
        ]
        return tableData
    }
    )

    const parseTableData = (apiData) => {
        getTreeData()
        let data = apiData
        let tempVersionedObject = {}

        for (let index in data) {
            const element = data[index];

            for (const individualPiece in element) {
                const dataPiece = element[individualPiece]
                tempVersionedObject[individualPiece] = { id: individualPiece, ...dataPiece } //combining all into one array
            }
        }
        const sortedKeys = Object.keys(tempVersionedObject).sort();

        // Create a new object with sorted keys
        const sortedDemoData = {};
        sortedKeys.forEach(key => {
            sortedDemoData[key] = tempVersionedObject[key];
        });

        tableData.value = sortedDemoData
    }

    const selectTableFilter = ((option) => {
        selectedOption.value = option
    })

    const fetchData = async (lineageID) => {
        try {
            const response = await axios.get(`https://develop.pistis-market.eu/srv/lineage-tracker/get_dataset_family_tree?uuid=${lineageID}`, {
                headers: {
                    'Authorization': `Bearer ${authStore.user.token}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });
            treeObject.value = await response.data
            familyTreeData.value = await response.data
            parseTableData(treeObject.value)
            console.log('API response:', response.data);

        } catch (error) {
            console.error('API request failed:', error);
        }
    }


    return { fetchData, sampleDiffStorage, displayState, resetDiff, addtoDiff, selectedDiff, treeObject, parseTableData, tableData, selectedOption, isCompareVisible, navigation, subNav, openCompare, getTreeData, familyTreeData, getDatasetHistory, selectTableFilter }
})
