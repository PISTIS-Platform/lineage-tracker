<template>
    <div id="tree-simple" class="chart" ref="treeContainer"></div>
  </template>
  
  <script>
  import { ref, watch, onMounted, nextTick } from 'vue';
  
  export default {
    name: 'TreeComponent',
    props: ['data', 'addToDiff', 'selectedDiff'],
    setup(props) {
      const treeContainer = ref(null);
      let initialized = false;  // Track if chart is already initialized
  
      // Function to create or update the Treant chart
      const createOrUpdateChart = () => {
        if (!treeContainer.value) return;
  
        // Clear existing chart only if not already initialized
        if (!initialized) {
          treeContainer.value.innerHTML = '';
        }
  
        const data = props.data;
  
        // Create node map
        const nodeMap = {};
  
        // Populate node map and link children to parents
        Object.values(data).forEach(group => {
          Object.keys(group).forEach(id => {
            const node = group[id];
            nodeMap[id] = { id, ...node, children: [] };
          });
        });
  
        Object.values(nodeMap).forEach(node => {
          if (node.derived_from) {
            const parent = nodeMap[node.derived_from];
            if (parent) {
              parent.children.push(node);
            }
          }
        });
  
        // Identify root nodes
        const rootNodes = Object.values(nodeMap).filter(node => !node.derived_from);
  
        // Convert root nodes to Treant format with node buttons
        const convertToTreantFormat = (node) => {
          return {
            innerHTML: `<button class="node_button test_tooltip ${props.selectedDiff.includes(node.version) ? 'active' : ''}" type="button" data-id="${node.version}">v${node.version}
              <span class="tooltiptext">
                <ul class="text-align-left">
                  <li class=>UUID: ${node.id}</li>
                  <li>Version: ${node.version}</li>
                  <li>Operation: ${node.operation_description} Dataset</li>
                  <li>Timestamp: ${node.timestamp}</li>
                </ul>
              </span>
            </button>`,
            children: node.children.map(convertToTreantFormat)
          };
        };
  
        const treantData = rootNodes.map(convertToTreantFormat);
  
        // Set the nodeStructure
        const chartConfig = {
          chart: {
            container: "#tree-simple",
          },
          nodeStructure: treantData[0],
        };
  
        // Initialize or reinitialize the Treant.js tree
        if (!initialized) {
          new Treant(chartConfig);
          initialized = true; // Mark chart as initialized after the first render
        }
  
        // Event delegation for button clicks
        treeContainer.value.addEventListener('click', (event) => {
          if (event.target.matches('.node_button')) {
            const id = event.target.getAttribute('data-id');
            if (id) {
              handleNodeClick(id);
            }
          }
        });
      };
  
      const handleNodeClick = (id) => {
        // if (!props.selectedDiff.includes(id)) {
        //   props.addToDiff(id);  // Only add to selectedDiff if not already present
        // }
          props.addToDiff(id);
      };
  
      // Watch for changes in selectedDiff and re-render the buttons
      watch(() => props.selectedDiff, () => {
        nextTick(() => {
          updateButtonHighlighting(); // Update the button highlighting when selectedDiff changes
        });
      }, { deep: true });
  
      //Update button highlighting without re-rendering the whole chart
      const updateButtonHighlighting = () => {
        const buttons = treeContainer.value.querySelectorAll('.node_button');
        buttons.forEach(button => {
          const id = button.getAttribute('data-id');
          if (props.selectedDiff.includes(id)) {
            button.classList.add('active');
          } else {
            button.classList.remove('active');
          }
        });
      };
  
      onMounted(() => {
        createOrUpdateChart();
      });
  
      return { treeContainer };
    },
  };
  </script>
  
  <style>
  .node_button {
    width: 45px;
    height: 43px;
    border-radius: 50%;
    background-color: #5632d0;
    border: 2.7px solid #fff;
    color: #fff;
    font-size: .5rem;
    box-shadow: 0 0 0 1.3px #898989;
    z-index: 13;
    cursor: pointer;  
  }
  
  .node_button.active {
    background-color: red;
    color: white;
  }
  
  .test_tooltip {
    position: relative;
    display: inline-block;
  }
  
  .test_tooltip .tooltiptext {
    visibility: hidden;
    width: 120px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px 0;
    margin: .3rem;
    position: absolute;
    z-index: 1;
    top: -5px;
    left: 105%;
  }

  #tree-simple{
    overflow: hidden;
  }
  
  .test_tooltip:hover .tooltiptext {
    visibility: visible;
  }
  
  .tooltiptext ul {
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: .2rem;
  }
  </style>
    