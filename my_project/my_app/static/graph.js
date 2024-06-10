function drawGraph(filePath) {
    // Функция для загрузки XML-файла
    function loadXMLFile(filePath, callback) {
        fetch(filePath)
            .then(response => response.text())
            .then(data => {
                const parser = new DOMParser();
                const xmlDoc = parser.parseFromString(data, 'application/xml');
                callback(xmlDoc);
            })
            .catch(error => {
                console.error('Error fetching or parsing XML:', error);
            });
    }

    // Функция для создания графа из XML
    function createGraphFromXML(xmlDoc) {
        const nodes = [];
        const links = [];

        xmlDoc.querySelectorAll('mxCell').forEach(cell => {
            const id = cell.getAttribute('id');
            const value = cell.getAttribute('value');
            const source = cell.getAttribute('source');
            const target = cell.getAttribute('target');

            if (value) {
                nodes.push({ id, value });
            }

            if (source && target) {
                links.push({ source, target });
            }
        });

        return { nodes, links };
    }

    // Функция для визуализации графа
    function visualizeGraph(graph) {
        const width = 800;
        const height = 600;

        const svg = d3.select('#graph').append('svg')
            .attr('width', width)
            .attr('height', height);

        const simulation = d3.forceSimulation(graph.nodes)
            .force('link', d3.forceLink(graph.links).id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2));

        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(graph.links)
            .enter().append('line')
            .attr('class', 'link');

        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(graph.nodes)
            .enter().append('g')
            .attr('class', 'node');

        node.append('circle')
            .attr('r', 10);

        node.append('text')
            .attr('x', 12)
            .attr('dy', '.35em')
            .text(d => d.value);

        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }

    // Загружаем XML-файл и визуализируем граф
    loadXMLFile(filePath, xmlDoc => {
        const graph = createGraphFromXML(xmlDoc);
        visualizeGraph(graph);
    });
}