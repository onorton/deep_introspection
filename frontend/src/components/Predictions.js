import React, { Component } from 'react';
import { Spinner } from  "@blueprintjs/core";
import {MainToaster} from '../MainToaster'

export default class Predictions extends Component {

  render(){
    const array = [0,1,2,3,4]
    return (
      <div style={this.props.style}>
      {this.props.predictions.length == 0 ?
        <ul style={{listStyleType: 'none', height:100, padding: '0 20px 0 20px', position: 'relative'}}>
        {array.map(function(bar, index) {
        return(<li className='pt-skeleton' style={{width:'100%', margin:"5px 0px 5px 0px", backgroundImage: 'linear-gradient(to right, rgba(0, 190, 0, 1), rgba(0, 190, 0, 1))', backgroundRepeat: 'no-repeat', backgroundSize: 20*(5-index)+'%'}}>_</li>)
      })
        }
        </ul>
      :
      <ul style={{listStyleType: 'none', height:this.props.predictions.length*20, padding: '0 20px 0 20px', position: 'relative'}}>
      {
        this.props.predictions.map(function(prediction, index) {
          return(<li style={{width:'100%', margin:"5px 0px 5px 0px", backgroundImage: 'linear-gradient(to right, rgba(0, 190, 0, 1), rgba(0, 190, 0, 1))', backgroundRepeat: 'no-repeat', backgroundSize: 100*prediction.value+'%'}}>{prediction.label + ': ' + (100*prediction.value).toFixed(2) + '%'}</li>)
        })
      }
      </ul>}
      </div>
    )
  }
}
