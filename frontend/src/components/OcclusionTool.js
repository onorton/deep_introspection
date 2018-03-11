import React, { Component } from 'react';

export default class OcclusionTool extends Component {

  constructor(props) {
    super(props);
    this.state = {
      features: [],
      predictions: [],
      image: null
    };
  }
  componentWillReceiveProps(nextProps) {
    this.fetchFeatures(nextProps.testModel.id, nextProps.testImage.id)
  }
  componentDidMount() {
    this.fetchFeatures(this.props.testModel.id, this.props.testImage.id)
  }

  fetchFeatures(model, image) {
    const tool = this
    fetch('http://127.0.0.1:8000/features/' + model + '/' + image, {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          const features = data.features.map(function(feature) {return {feature: feature, active: true}})
          tool.setState({features: features})
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }

  toggle(index) {
    const tool = this
    var features = this.state.features
    features[index].active = !features[index].active
    this.setState({features: features})
    const inactiveFeatures = features.filter(feature => !feature.active).map(feature => feature.feature)
    fetch('http://127.0.0.1:8000/features/evaluate/' + this.props.testModel.id + '/' +  this.props.testImage.id, {
      method: 'POST',
      body: JSON.stringify({inactiveFeatures: inactiveFeatures}),
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {

      if (response.status == 200) {
        response.json().then(function(data) {
          tool.setState({predictions: data.predictions, image: data.image})
        })
      }
  }).catch(function(error) {
    console.log('There has been a problem with your fetch operation: ' + error.message);
  });
}
  render(){
    const tool = this
    return (
    <div className="toolArea">
    <ul style={{listStyleType: 'none', padding: 0, marginLeft:10, float:'left'}}>
    {this.state.features.map(function(feature, index) {

         const activeFeature = <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-active pt-intent-primary " onClick={() => tool.toggle(index)}>Feature {feature.feature}</label></li>
         const inactiveFeature =  <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-intent-primary" onClick={() => tool.toggle(index)}>Feature {feature.feature}</label></li>
        return (feature.active) ? activeFeature : inactiveFeature
    })}
    </ul>
    <div className="results" style={{ float:"right", marginRight:20}}>
    {(this.state.image != undefined) ? <img src={this.state.image} style={{maxWidth:300, maxHeight:300, borderStyle:"solid", borderColor:"#10161A"}}/> : <img src={this.props.testImage.url} style={{maxWidth:300, maxHeight:300, borderStyle:"solid", borderColor:"#10161A"}}/>}
    <ul style={{listStyleType: 'none'}}>
    {
      this.state.predictions.map(function(prediction, index) {
        return(<li style={{width:'100%', backgroundImage: 'linear-gradient(to right, rgba(0, 190, 0, 1), rgba(0, 190, 0, 1))', backgroundRepeat: 'no-repeat', backgroundSize: 100*prediction.value+'%'}}>{prediction.label + ': ' + (100*prediction.value).toFixed(2) + '%'}</li>)
      })
    }
    </ul>
    </div>
    </div>
    )
  }
}
