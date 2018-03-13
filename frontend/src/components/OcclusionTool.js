import React, { Component } from 'react';

export default class OcclusionTool extends Component {

  constructor(props) {
    super(props);
    this.state = {
      features: [],
      predictions: [],
      image: null,
      hover: null
    };
  }
  componentWillReceiveProps(nextProps) {
    this.setState({image: nextProps.testImage.url, predictions: [], features: []})
    this.fetchFeatures(nextProps.testModel.id, nextProps.testImage.id)
  }
  componentDidMount() {
    this.setState({image: this.props.testImage.url, predictions: [], features:[]})
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
          tool.setState({features: features}, () => tool.fetchPredictions())
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }

  toggle(index) {
    var features = this.state.features
    features[index].active = !features[index].active
    this.setState({features: features}, () => this.fetchPredictions())
  }

  fetchPredictions() {
    const features = this.state.features
    const tool = this
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
    console.log(this.state.predictions)
    return (
    <div className="toolArea">
    <ul style={{listStyleType: 'none', padding: 0, marginLeft:10, float:'left'}}>
    {this.state.features.map(function(feature, index) {

         const activeFeature = <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-active pt-intent-primary " onClick={() => tool.toggle(index)} onMouseOver={() => tool.setState({hover: index})} onMouseLeave={() => tool.setState({hover: null})}>Feature {feature.feature}</label></li>
         const inactiveFeature =  <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-intent-primary" onClick={() => tool.toggle(index)} onMouseOver={() =>  tool.setState({hover: index})} onMouseLeave={() => tool.setState({hover: null})}>Feature {feature.feature}</label></li>
        return (feature.active) ? activeFeature : inactiveFeature
    })}
    </ul>
    <div className="results" style={{ float:"right", width: 400, marginRight:20, height:600}}>
    <div style={{position:'relative'}}>
    <img src={this.state.image} style={{width:'100%', borderStyle:"solid", borderColor:"#10161A", zIndex:0,position:'relative', top: 0, left: 0}}/>
    {(this.state.hover != null) ? <img src={'media/features/feature_model_'+ this.props.testModel.id + '_image_' + this.props.testImage.id + '_' + this.state.hover + '.png'} style={{width:'100%', borderStyle:"solid", borderColor:"#10161A", zIndex:1, position:'absolute', top: 0, left: 0}}/> : <div/>}

    </div>
    <ul style={{listStyleType: 'none', height:100, padding: '0 20px 0 20px', position: 'relative'}}>
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
