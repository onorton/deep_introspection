import React, { Component } from 'react';

export default class Predictions extends Component {

  render(){
    return (
      <ul style={{listStyleType: 'none', height:100, padding: '0 20px 0 20px', position: 'relative'}}>
      {
        this.props.predictions.map(function(prediction, index) {
          return(<li style={{width:'100%', backgroundImage: 'linear-gradient(to right, rgba(0, 190, 0, 1), rgba(0, 190, 0, 1))', backgroundRepeat: 'no-repeat', backgroundSize: 100*prediction.value+'%'}}>{prediction.label + ': ' + (100*prediction.value).toFixed(2) + '%'}</li>)
        })
      }
      </ul>
    )
  }
}
