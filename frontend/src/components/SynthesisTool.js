import React, { Component } from 'react';

export default class SynthesisTool extends Component {

  render(){
    return (
    <div className="toolArea">
    {(this.props.testImage != undefined) ? <img src={this.props.testImage} style={{maxWidth:300, maxHeight:300, float:"right", marginRight:20, borderStyle:"solid", borderColor:"#10161A"}}/> : <div/>}
    </div>
    )
  }
}
