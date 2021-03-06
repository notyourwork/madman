function init() {

        /* 1) Create a new SnowflakeLayout.
         * 
         * If you're going to place the graph in an HTML Element, other
         * the <body>, remember that it must have a known size and
         * position (via element.offsetWidth, element.offsetHeight,
         * element.offsetTop, element.offsetLeft).
         */
        var layout = new ForceDirectedLayout( document.body, true );
        
        layout.config._default = {
                model: function( dataNode ) {
                        return {
                                mass: .5
                        }
                },
                view: function( dataNode, modelNode ) {
                        if ( layout.svg ) {
                                var nodeElement = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                                nodeElement.setAttribute('stroke', '#888888');
                                nodeElement.setAttribute('stroke-width', '.25px');
                                nodeElement.setAttribute('fill', dataNode.color);
                                nodeElement.setAttribute('r', 10 + 'px');
                                nodeElement.onmousedown =  new EventHandler( layout, layout.handleMouseDownEvent, modelNode.id )
                                return nodeElement;
                        } else {
                                var nodeElement = document.createElement( 'div' );
                                nodeElement.style.position = "absolute";
                                nodeElement.style.width = "20px";
                                nodeElement.style.height = "20px";
                                
                                var color = dataNode.color.replace( "#", "" );
                                nodeElement.style.backgroundImage = "url(http://kylescholz.com/cgi-bin/bubble.pl?title=&r=20&pt=8&b=888888&c=" + color + ")";
                                nodeElement.innerHTML = '<img width="1" height="1">';
                                nodeElement.onmousedown =  new EventHandler( layout, layout.handleMouseDownEvent, modelNode.id )
                                return nodeElement;
                        }
                }
        }

layout.forces.spring._default = function( nodeA, nodeB, isParentChild ) {
                return {
                        springConstant: 0.2,
                        dampingConstant: 0.2,
                        restLength: 60
                }
        }
        
layout.forces.magnet = function() {
                return {
                        magnetConstant: -4000,
                        minimumDistance: 40
                }
        }

        
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
                                'pixelColor': dataNodeSrc.color,
                                'pixelWidth': '2px',
                                'pixelHeight': '2px',
                                'pixels': 10
                        }
                }
        }

        /* 4) Load up some stuff by hand
         * 
         */
        
        layout.model.ENTROPY_THROTTLE=false;

        var nodes = [];
        for ( var i=0; i<60; i++ ) {
                var node = new DataGraphNode();
                node.color= (Math.random()>.5) ? "#8888bb" : "#bb8888";
                node.mass=.5;
                layout.newDataGraphNode( node );

                if ( nodes.length>0 ) {
                        var neighbor = nodes[Math.floor((Math.random()*nodes.length))];
                        layout.newDataGraphEdge( node, neighbor );							
                }

                if ( nodes.length>0 && Math.random() >.6 ) {
                        var neighbor = nodes[Math.floor((Math.random()*nodes.length))];
                        layout.newDataGraphEdge( node, neighbor );							
                }

                nodes.push( node );
        }

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
