import React from 'react';

import { List } from 'immutable';

interface Feed {
    id: number;
    name: string;
};

interface Zone {
    x: number;
    y: number;
    width: number;
    height: number;
    name: string;
    displaystyle: "scrolling_h"|"scrolling_v"|"fading";
    feeds: List<Feed>; //Feed[];
};
function defaultZone(): Zone {
    return {x:100,
            y: 100,
            width: 100,
            height: 100,
            name: "New Zone",
            displaystyle: "fading",
            feeds: List(),
            };
};

export interface Layout {
    id: number;
    name: string;
    slug: string;
    background_url: string;
    zones: List<Zone>; //Zone[];
};

/* Component stuff */

interface Props {
    id: number;
};

interface State {
    layout: Layout;
    //////
    selected_zone_index: number|null;
    display_mode: "JSON"|"Graphical";
    aspect_ratio: number,
    display_width: number,
    display_height: number,
    drag_start: boolean,

};

export class LayoutEditor extends React.Component<Props, State> {

    constructor(args: any) {
        super(args);
        this.state = {
            layout: {
                id: -1,
                name: '',
                slug: '',
                background_url: '',
                zones: List(),
            },
            selected_zone_index: null,
            display_mode: "Graphical",
            aspect_ratio: 1.77777777,
            display_width: 0,
            display_height: 0,
            drag_start: false,
        };

        this.getFromServer(args.match.params.id);
    }


    /* My Methods */

    async getFromServer(id: number) {
        const resp = await fetch('/layout_' + id + '.json');
        const json = await resp.json() as Layout;
        this.setState({layout: json as Layout});
        this.setState({layout: { ...json, zones: List()}});
    };

    addZone() {
        this.setState((state, _) => ({
            layout: {...state.layout,
                     zones: state.layout.zones.push(defaultZone())} as Layout
        }));
    }

    selectZone(index:number|null) {
        this.setState({selected_zone_index: index});
    }

    resizeZone(x: number,y: number,w: number,h: number) {
        this.setState((state, _) => {
            if (state.selected_zone_index === null) {
                return null;
            }
            const active_zone = {...state.layout.zones.get(state.selected_zone_index),
                                x:x, y:y, width:w, height:h} as Zone;
            return {
                layout: {...state.layout,
                         zones: state.layout.zones.set(state.selected_zone_index, active_zone) }
            };
            });
        };

    recvUpdate(cb: (state: State, other: any)=>any) {
        this.setState(cb);
    }

    clickOnLayout() {
        // the onClick for the whole Layout Box.
        // Either deselect the current Zone if clicked on bg, else
        // ignore.
        return (evt: {target: any}) => {
            if (evt.target.classList.contains('click_deselects')) {
                this.selectZone(null);
            }
            return false;
        }
    }

    layoutStyle(): any {
        return {height: this.state.display_height};
    }

    zoneStyle(zone: Zone): any {
        return {
            position: 'absolute',
            top: zone.y,
            left: zone.x,
            width: zone.width,
            height: zone.height,
        };
    }

    updateDimensions() {
        const w:number = (document as any).getElementById('layout_box').offsetWidth;
        this.setState({
            display_width: w,
            display_height: w / this.state.aspect_ratio,
        });
    };

    /* React Methods */

    componentDidMount() {
        this.updateDimensions();
        window.addEventListener("resize", this.updateDimensions.bind(this)); 
    }
    componentWillUnmount() {
        window.removeEventListener("resize", this.updateDimensions.bind(this));
    }

    render() {
        return (<div>
            <button onClick={()=>this.addZone()}>+</button>{ this.state.display_height }
            <div id="layout_box" style={ this.layoutStyle() } onClick={ this.clickOnLayout() } className="click_deselects">
            {this.state.layout.zones.map((zone: Zone, index: number) => (
                <div key={index} className="zone" style={this.zoneStyle(zone)} onClick={ ()=> this.selectZone(index) }>{zone.name}</div>
            ))}
            { (this.state.selected_zone_index !== null) &&
                <SelectedZone
                    zone={this.state.layout.zones.get(this.state.selected_zone_index) as Zone}
                    onUpdate={ (a,b,c,d) => (this.resizeZone(a,b,c,d)) }
                    onDeselect={ this.clickOnLayout() }
                    />
            }

            </div>
        </div>);
    }
}


enum SZMode {
    Nothing = 0,
    Move,
    TopResize,
    BottomResize,
    LeftResize,
    RightResize,
}

interface SZProps{
    zone: Zone,
    onUpdate:(x:number,y:number,w:number,h:number)=>void,
    onDeselect:(target:any)=>any,
}

interface SZState {
    mode: SZMode,
    initial_x: number,
    initial_y: number,
}

class SelectedZone extends React.Component<SZProps, SZState> {
    constructor(args: any) {
        super(args);
        this.state = {mode: SZMode.Nothing, initial_x: 0, initial_y: 0};
    }

    move_mousedown() {
        return (evt:any) => {
            this.setState({initial_x: evt.clientX, initial_y: evt.clientY, mode:SZMode.Move});
        }
    }
    resizetop_mousedown() {
        return (evt:any) => {
            this.setState({initial_x: evt.clientX, initial_y: evt.clientY, mode:SZMode.TopResize});
        }
    }
    resizebottom_mousedown() {
        return (evt:any) => {
            this.setState({initial_x: evt.clientX, initial_y: evt.clientY, mode:SZMode.BottomResize});
        }
    }
    resizeleft_mousedown() {
        return (evt:any) => {
            this.setState({initial_x: evt.clientX, initial_y: evt.clientY, mode:SZMode.LeftResize});
        }
    }
    resizeright_mousedown() {
        return (evt:any) => {
            this.setState({initial_x: evt.clientX, initial_y: evt.clientY, mode:SZMode.RightResize});
        }
    }

    onMouseMove() {
        return (evt: any) => {
                switch (this.state.mode) {
                    case SZMode.Move:
                        this.props.onUpdate(
                            Math.max(0, this.props.zone.x - (this.state.initial_x - evt.clientX)),
                            Math.max(0, this.props.zone.y - (this.state.initial_y - evt.clientY)),
                            this.props.zone.width,
                            this.props.zone.height);
                        this.setState({initial_x: evt.clientX, initial_y: evt.clientY});
                        break;
                    default:
                        break;
                }
        };
    }

    move_mouseup() {
        return (evt: any) => {
            this.setState({mode: SZMode.Nothing});
        }
    }

    zoneStyle() {
        return {
            color:'pink',
            top: this.props.zone.y,
            left: this.props.zone.x,
            width: this.props.zone.width,
            height: this.props.zone.height,
        }
    }
    zoneResizeTopStyle() {

    }
    render() {
        return(
            <div id="zone_resizer_bg"
                onMouseMove={ this.onMouseMove() }
                 onClick={ this.props.onDeselect }
                 className="click_deselects">
                <div id="zone_position_info">{this.props.zone.x}, { this.props.zone.y }</div>

                <div id="zone_resize_top"
                     className="zone_resizer"
                     onMouseDown={this.resizetop_mousedown()}
                     style={{ top: this.props.zone.y - 15,
                             left: this.props.zone.x,
                             width: this.props.zone.width }}></div>
                <div id="zone_resize_btm"
                     className="zone_resizer"
                     style={{ top: this.props.zone.y + this.props.zone.height,
                             left: this.props.zone.x,
                             width: this.props.zone.width }}></div>
                <div id="zone_resize_left"
                     className="zone_resizer"
                     style={{ top: this.props.zone.y,
                             left: this.props.zone.x - 15,
                             height: this.props.zone.height }}></div>
                <div id="zone_resize_right"
                     className="zone_resizer"
                     style={{ top: this.props.zone.y,
                             left: this.props.zone.x + this.props.zone.width,
                             height: this.props.zone.height }}></div>
                <div id="zone_mover"
                     style={ this.zoneStyle() }
                     draggable
                     onMouseDown={this.move_mousedown()}
                     onMouseUp={this.move_mouseup()}>
                        Selected zone: { this.props.zone.name }</div>
            </div>
        );
    };
}

export default LayoutEditor;
