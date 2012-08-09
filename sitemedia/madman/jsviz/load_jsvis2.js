
function init() {

	/* 1) Create a new SnowflakeLayout.
	 * 
	 * If you're going to place the graph in an HTML Element, other
	 * the <body>, remember that it must have a known size and
	 * position (via element.offsetWidth, element.offsetHeight,
	 * element.offsetTop, element.offsetLeft).
	 */
	var layout = new ForceDirectedLayout( document.body, true );
	layout.view.skewBase=575;
	layout.setSize();

	/* 2) Configure the layout.
	 * 
	 * This configuration defines how we handle the addition of
	 * different kinds of nodes to the graph. For each "type" of
	 * node, we tell the layout how to create a "model" and "view"
	 * of the new node.
	 */
	layout.config._default = {
		
	/* The "model" defines the underlying structure of our graph.
	 * For a SnowflakeModel, we need to define the following for
	 * each node:
	 * 
	 * - childRadius: the edge length to this node's children
	 * - fanAngle: the maximum angle in which child nodes will be
	 *   layed out
	 * - rootAngle: the base angle of the graph at the origin (this
	 *   is automatically determined for all child nodes)
	 * 
	 * These parameters determine how this new node will interact
	 * with other nodes in our graph. The "model" attribute of a
	 * class in our configuration must return a JavaScript Object
	 * containing these values.
	 */
	
		model: function( dataNode ) {
			return {
				mass: 4
			}
		},
		
	/* The "view" defines what the nodes in our graph look like.
	 * The "view" attribute of a class must return a DOM element -- 
	 * JSViz supports most HTML and SVG elements. You can control
	 * the appearence and behavior of view elements just like any
	 * DOM element: 
	 * 
	 * CSS: Point to a CSS style sheet using the "className"
	 * attribute of the DOM element.
	 * 
	 * Contents: Indicate the node's contents, in HTML, using the
	 * "appendChild" function or by setting DOM element's innerHTML.
	 * 
	 * Behavior: Add an event handler using the EventHandler factory
	 * class. For example: 
	 * 
	 * nodeElement.onclick = new EventHandler( _caller, _handler, arg0, arg1... );
	 * 
	 * where _caller is an object instance that _handler may refer
	 * to as "this" (use "window" if the function is in the global
	 * scope), _handler is the function to be executed, and any
	 * additional arguments are passed as parameters to _handler. 
	 */

		view: function( dataNode, modelNode ) {
			if ( layout.svg ) {
				var nodeElement = document.createElementNS("http://www.w3.org/2000/svg", "circle");
				nodeElement.setAttribute('stroke', '#888888');
				nodeElement.setAttribute('stroke-width', '.25px');
				nodeElement.setAttribute('fill', dataNode.color);
				nodeElement.setAttribute('r', 16 + 'px');
				nodeElement.onmousedown =  new EventHandler( layout, layout.handleMouseDownEvent, modelNode.id )
				return nodeElement;
			} else {
				var nodeElement = document.createElement( 'div' );
				nodeElement.style.position = "absolute";
				nodeElement.style.width = "auto";
				nodeElement.style.height = "auto";
				
				var color = dataNode.color.replace( "#", "" );
				if (dataNode.fixed) {
					nodeElement.style.background = "#aaaaaa";
					nodeElement.style.border = "solid 2px #777777";
				} else {
					nodeElement.style.background = "#dddddd";
					nodeElement.style.border = "solid 2px #aaaaaa";
				}

				nodeElement.style.cursor = "pointer";
				nodeElement.style.padding = "7px";
				//nodeElement.innerHTML = '<img width="1" height="1">';
				nodeElement.innerHTML = dataNode.desc;
				nodeElement.onmousedown =  new EventHandler( layout, layout.handleMouseDownEvent, modelNode.id )
				
				// set edges color
				switch (dataNode.iweight) {
				    case '-3': nodeElement.setAttribute('edgeColor', '#ff0000'); 
					         nodeElement.setAttribute('edgeWidth', '12px'); 
							 break;
				    case '-2': nodeElement.setAttribute('edgeColor', '#ff0000'); 
					         nodeElement.setAttribute('edgeWidth', '6px'); 
							 break;
					case '-1': nodeElement.setAttribute('edgeColor', '#ff0000'); 
					         nodeElement.setAttribute('edgeWidth', '3px'); 
							 break;
					case '1':  nodeElement.setAttribute('edgeColor', '#00ff00'); 
					         nodeElement.setAttribute('edgeWidth', '3px'); 
							 break;										 
				    case '2':  nodeElement.setAttribute('edgeColor', '#00ff00'); 
					         nodeElement.setAttribute('edgeWidth', '6px'); 
							 break;						
				    case '3':  nodeElement.setAttribute('edgeColor', '#00ff00'); 
					         nodeElement.setAttribute('edgeWidth', '12px'); 
							 break;						
				}							
				return nodeElement;
			}
		}
	}

	/* Force Directed Graphs are a simulation of different kinds of
	 * forces between particles. In JSViz, a graph edge is typically
	 * represented as an attractive "spring" force connecting
	 * two nodes.
	 * 
	 * It's often the case that parent-child relationships are
	 * represented with stricter force rules. This can help a graph
	 * organize with fewer overlapping edges.
	 */
	
layout.forces.spring._default = function( nodeA, nodeB, isParentChild ) {
		if (isParentChild) {
			return {
				springConstant: 0.5,
				dampingConstant: 0.2,
				restLength: 60
			}
		} else {
			return {
				springConstant: 0.2,
				dampingConstant: 0.2,
				restLength: 60
			}
		}
	}
	
	/* Note that there is no need to include the above function in
	 * your application if you're satisfied with the default
	 * behavior.
	 * 
	 * You may wish to represent different edge weights in your
	 * graph with different edge lengths. A number of factors
	 * contribute to the actual edge length, but you can incluence
	 * the graph by applying different spring confiugrations between
	 * different kinds of edges.
	 * 
	 * For example, to apply a looser relationship beween node types
	 * 'A' and 'B', I can create a custom spring with greater
	 * elasticity:
	 */

	layout.forces.spring['A'] = {};
layout.forces.spring['A']['B'] = function( nodeA, nodeB, isParentChild ) {
		return {
			springConstant: 0.4,
			dampingConstant: 0.2,
			restLength: 420
		}
	}
	/* Note that these configurations are directed: The above
	 * configuration would apply to an edge from a node of type
	 * 'A' to a node of type 'B', but not from a 'B' to an 'A' ...
	 * use a additional configuration from that. 
	 */
	
	/* The other forces in our graph repel each node from another.
	 * This function should be the same for all node types.
	 */
layout.forces.magnet = function() {
		return {
			magnetConstant: -2000,
			minimumDistance: 10
		}
	}
	
	/* You don't need to include the above function in your
	 * application if you are satisfied with the default
	 * implementation.
	 */
	
	/* 3) Override the default edge properties builder.
	 * 
	 * @return DOMElement
	 */ 
	layout.viewEdgeBuilder = function( dataNodeSrc, dataNodeDest ) {
		if ( this.svg ) {
			return {
				'stroke': dataNodeSrc.color,
				'stroke-width': '2px',
				'stroke-dasharray': '2,4'
			}
		} else {
			return {
				'pixelColor': dataNodeSrc.edgeColor,
				'pixelWidth': dataNodeSrc.edgeWidth,
				'pixelHeight': dataNodeSrc.edgeWidth,
				'pixels': 10
			}
		}
	}

	/* 4) Make an loader to process the contents of our file.
	 * 
	 * Here, we're using the XML Loader. 
	 */
	var loader = new XMLTreeLoader( layout.dataGraph );
	loader.load( "treedata1.xml" );

	/* 5) Control the addition of nodes and edges with a timer.
	 * 
	 * This enables the graph to start organizng as data is loaded.
	 * Use a larger tick time for smoother animation, but slower
	 * build time.
	 */
	var buildTimer = new Timer( 150 );
	buildTimer.subscribe( layout );
	buildTimer.start();
}

