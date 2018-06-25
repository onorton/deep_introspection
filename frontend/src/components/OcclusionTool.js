import React, { Component } from 'react';
import OcclusionResult from './OcclusionResult'
import Predictions from './Predictions'
import { Tooltip, Position, Intent, Spinner} from  "@blueprintjs/core";
import OcclusionFeedback from './OcclusionFeedback'
import {MainToaster} from '../MainToaster'
import { Scrollbars } from 'react-custom-scrollbars';

export default class OcclusionTool extends Component {

  constructor(props) {
    super(props);
    this.state = {
      features: [],
      predictions: [],
      image: null,
      hover: null,
      results: null,
      feedback: false,
      analysing: false,
    };
  }
  componentWillReceiveProps(nextProps) {
    if (this.props.testImage.id != nextProps.testImage.id || this.props.testModel.id != nextProps.testModel.id) {
      this.setState({image: nextProps.testImage.url, predictions: [], features: [], results: null, analysing: false})
      this.fetchFeatures(nextProps.testModel.id, nextProps.testImage.id)
    }
  }
  componentDidMount() {
    this.setState({image: this.props.testImage.url, predictions: [], features: [], results: null, analysing: false})
    this.fetchFeatures(this.props.testModel.id, this.props.testImage.id)
  }

  fetchFeatures(model, image) {
    const tool = this
    fetch('/features/' + model + '/' + image, {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          const features = data.features.map(function(feature) {return {feature: feature, active: true}})
          tool.setState({features: features, image:data.image}, () => tool.fetchPredictions())
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
    tool.setState({predictions: []})
    MainToaster.show({ timeout:5000, intent: Intent.PRIMARY, message: "Calculating new predictions..." });
    fetch('/features/evaluate/' + this.props.testModel.id + '/' +  this.props.testImage.id, {
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


  analyse() {
    const tool = this
    MainToaster.show({ timeout:5000, intent: Intent.PRIMARY, message: "Analysing occlusions" });
    tool.setState({analysing:true})
    fetch('/features/analyse/' + this.props.testModel.id + '/' +  this.props.testImage.id, {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      }
    }).then(function(response) {

      if (response.status == 200) {
        response.json().then(function(data) {
          tool.setState({results: data.results})
        })
      }
  }).catch(function(error) {
    console.log('There has been a problem with your fetch operation: ' + error.message);
  });
  }



  render(){
    const tool = this
    const placeholderFeatures = [0,1,2,3,4,5]
    return (
    <div className="toolArea">
    <div className="buttonArea" style={{width:'100%'}}>
    <Tooltip style={{width:200}} content="Analyses model and image with various metrics. May take several minutes." position={Position.TOP}>
      <label className="pt-button pt-intent-primary pt-large " onClick={() => {this.analyse()}}>Analyse</label>
    </Tooltip>
    </div>


    <ul style={{listStyleType: 'none', padding: 0, marginLeft:10, float:'left'}}>
    {this.state.features.length == 0 ?
      placeholderFeatures.map(function(feature, index) {
         const placeholderFeature = <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-disabled pt-skeleton">Feature 0</label></li>
        return placeholderFeature
      })

      :this.state.features.map(function(feature, index) {

         const activeFeature = <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-active pt-intent-primary " onClick={() => tool.toggle(index)} onMouseOver={() => tool.setState({hover: index})} onMouseLeave={() => tool.setState({hover: null})}>Feature {feature.feature}</label></li>
         const inactiveFeature =  <li style={{padding: '5px 0px 5px 0px'}}><label className="pt-button pt-intent-primary" onClick={() => tool.toggle(index)} onMouseOver={() =>  tool.setState({hover: index})} onMouseLeave={() => tool.setState({hover: null})}>Feature {feature.feature}</label></li>
        return (feature.active) ? activeFeature : inactiveFeature
    })}
    </ul>

    <div className="results" style={{ float:"right", width: 400, marginRight:20, height:600}}>
    <div style={{position:'relative'}}>
    <img src={this.state.image} style={{width:'100%', borderStyle:"solid", borderColor:"#10161A", zIndex:0,position:'relative', top: 0, left: 0}}/>
    {(this.state.hover != null) ? <img src={'media/features/feature_model_'+ this.props.testModel.id + '_image_' + this.props.testImage.id + '_' + this.state.hover + '.png'} style={{width:'100%', zIndex:1, position:'absolute', top: 0, left: 0}}/> : <div/>}
    </div>
    <Predictions predictions={this.state.predictions}/>
    </div>


        {(this.state.results == null) ?
            (this.state.analysing) ?
            <div class="pt-spinner pt-large">
              <div class="pt-spinner-svg-container" style={{left:165, top:30}}>
                <svg viewBox="0 0 100 100">
                  <path class="pt-spinner-track" d="M 50,50 m 0,-44.5 a 44.5,44.5 0 1 1 0,89 a 44.5,44.5 0 1 1 0,-89"></path>
                  <path class="pt-spinner-head" d="M 94.5 50 A 44.5 44.5 0 0 0 50 5.5"></path>
                </svg>
              </div>
            </div>: <div/>
          :
          <Scrollbars  style={{height:730,width:600,left:165, marginLeft:'auto',marginRight:'auto',position:'relative'}}>
          <br/>
          <OcclusionResult
          features={this.state.features.map(function(feature) {return feature.feature})}
          testModel={this.props.testModel}
          testImage={this.props.testImage}
          results={this.state.results}/>

          <OcclusionFeedback isOpen={this.state.feedback} image={this.props.testImage} model={this.props.testModel} originalClass={this.state.results.originalClass} onClose={() => this.setState({feedback:false})}/>
          <label className="pt-button pt-intent-primary pt-large" onClick={() => {this.setState({feedback:true})}}>Feedback</label>
          </Scrollbars>
          }



    </div>
    )
  }
}
