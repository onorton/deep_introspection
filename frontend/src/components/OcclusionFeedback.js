import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'
import { Tab2, Tabs2, Slider, Checkbox, Radio, RadioGroup} from "@blueprintjs/core";
import PasswordMask from 'react-password-mask';

const initialState = {othersModified: false,
mfRequired: false,
mfPerturbation: false,
mi: false,
lc: false,
occlusionUseful: 3,
occlusionSpeed: 3,
exampleComments: '',
modelComments: '',
general: ''}

export default class OcclusionFeedback extends Component {


  constructor(props) {
    super(props);
    this.state = initialState;
    this.handleInputChange = this.handleInputChange.bind(this);
    this.occlusionUseful = this.occlusionUseful.bind(this);
    this.occlusionSpeed = this.occlusionSpeed.bind(this);

  }

  occlusionUseful(event) {
    this.setState({othersModified: true, occlusionUseful:event})
  }

  occlusionSpeed(event) {
    this.setState({othersModified: true, occlusionSpeed:event})
  }

  handleInputChange(event) {
   const target = event.target;
   const value = (target.type == 'checkbox') ? target.checked : target.value;
   const name = target.name;


   if (target.type == 'checkbox') {
     this.setState({othersModified: true})
   }

   this.setState({
     [name]: value
   })
 }

 readyToSubmit() {
   return (this.state.exampleComments != '' || this.state.modelComments != '' || this.state.general != '' || this.state.othersModified)
 }

  submit() {
    fetch('/evaluation/occlusion', {
      method: 'POST',
      body: JSON.stringify({image: this.props.image.id, model:this.props.model.id, state: this.state}),
      headers: {
          "Content-Type": "application/json"
      },
      credentials:'same-origin'

    }).then(function(response) {
      if (response.status == 200) {
        MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "Thanks for your feedback." });
      } else {
        throw Error(response.statusText);
      }

    }).catch(function(error) {
      MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "There was an issue in submitting your feedback." });
    });
    this.setState(initialState, this.props.onClose())

  }
  render() {
    return (
          <Dialog isOpen={this.props.isOpen} title="Occlusion Analysis Feedback"
            onClose={() => this.setState(initialState, this.props.onClose())}
            style={{backgroundColor:"#F5F8FA"}}
            canEscapeClose={true}
            canOutsideClickClose={true}
            isCloseButtonShown={true}>

              <div style={{padding:10}} className="pt-dialog-body">
              If you want to submit feedback on this particular occlusion analysis, you can do so here.
              <form style={{marginTop:10}}>

              <p>Overall, how useful was this analysis? (1 being not useful at all and 5 being very useful)</p>
              <Slider onChange={this.occlusionUseful} min={1} max={5} initialValue={1} value={this.state.occlusionUseful}/>

              <p>How fast was the analysis carried out? (1 being very slow and 5 being not noticeable)</p>
              <Slider onChange={this.occlusionSpeed} min={1} max={5} initialValue={1} value={this.state.occlusionSpeed}/>

              <p>Which of the four metrics did you find were helpful? (You may select more than one)</p>
              <Checkbox name="lc" checked={this.state.lc} onChange={this.handleInputChange}>Largest Change in Prediction</Checkbox>
              <Checkbox name="mi" checked={this.state.mi} onChange={this.handleInputChange}>Most Important Feature</Checkbox>
              <Checkbox name="mfRequired" checked={this.state.mfRequired} onChange={this.handleInputChange}>Minimal Features Required</Checkbox>
              <Checkbox name="mfPerturbation" checked={this.state.occlusionSupported} onChange={this.handleInputChange}>Minimal Features Perturbation</Checkbox>


              <p>Were you able to learn anything more about the test example from this analysis? </p>
              <textarea onChange={this.handleInputChange} name="exampleComments" class="pt-input pt-fill" dir="auto"></textarea>
              <br/>

              <p>Were you able to learn anything more about the model and the class "{this.props.originalClass}" from this analysis? </p>
              <textarea onChange={this.handleInputChange} name="modelComments" class="pt-input pt-fill" dir="auto"></textarea>
              <br/>

              If you have any other comments about this analysis and suggestions for improvement, you can provide them here:<br/>
              <textarea onChange={this.handleInputChange} name="general" class="pt-input pt-fill" dir="auto"></textarea>
              </form>
              </div>
              <div className="pt-dialog-footer" >
                             <div className="pt-dialog-footer-actions">
                             {(!this.readyToSubmit()) ? <button type="button" className="pt-button pt-intent-primary pt-disabled">Submit</button>:
                             <button type="button" className="pt-button pt-intent-primary" onClick={() => this.submit()}>Submit</button>}
                             </div>
                         </div>
          </Dialog>
    );
  }
}
