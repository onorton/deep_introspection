import React, { Component } from 'react';

export default class OcclusionResult extends Component {

  render(){
    return (
    <div>
    <h4>Occlusion Analysis</h4>
    The original class predicted for this image was {this.props.originalClass}.
    <h5>Largest Change in Prediction</h5>
    The features that are occluded to produce the largest change in probability for {this.props.originalClass} are {this.props.lc.features}.
    <h5>Most Important Feature</h5>
    The single feature that produces the largest change in probability for {this.props.originalClass} is feature {this.props.mi.feature}.
    <h5>Minimal Features Required</h5>
    The minimal features required to still predict {this.props.originalClass} are {(this.props.mfRequired.features.length > 0) ? this.props.mfRequired.features + '.' : 'none of those found.'}
    <h5>Minimal Features Perturbation</h5>
    The minimal features that need to be occluded so {this.props.originalClass} is not predicted are {this.props.mfPerturbation.features}.
    </div>
    )
  }
}
