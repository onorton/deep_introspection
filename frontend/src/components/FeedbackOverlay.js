import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'
import { Tab2, Tabs2, Slider, Checkbox, Radio, RadioGroup} from "@blueprintjs/core";
import PasswordMask from 'react-password-mask';

export default class FeedbackOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      othersModified: false,
      occlusionSupported: true,
      occlusionSupport: null,
      occlusionUseful: 3,
      occlusionSpeed: 3,
      occlusionFeatures: '',
      occlusionComments: '',
      synthesisSupported: true,
      synthesisSupport: null,
      synthesisUseful: 3,
      synthesisClose: 3,
      synthesisFeatures: '',
      synthesisComments: '',
      general: '',
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.occlusionUseful = this.occlusionUseful.bind(this);
    this.occlusionSpeed = this.occlusionSpeed.bind(this);
    this.synthesisUseful = this.synthesisUseful.bind(this);
    this.synthesisClose = this.synthesisClose.bind(this);
  }

  occlusionUseful(event) {
    this.setState({othersModified: true, occlusionUseful:event})
  }

  occlusionSpeed(event) {
    this.setState({othersModified: true, occlusionSpeed:event})
  }

  synthesisUseful(event) {
    this.setState({othersModified: true, synthesisUseful:event})
  }

  synthesisClose(event) {
    this.setState({othersModified: true, synthesisClose:event})
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
   return (this.state.occlusionFeatures != '' || this.state.occlusionComments != '' || this.state.synthesisFeatures != '' || this.state.synthesisComments != ''  || this.state.general != '' || this.state.othersModified)
 }

  submit() {
    fetch('/evaluation/general', {
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
    this.setState({othersModified: false, occlusionUseful: 3, occlusionSpeed: 3, occlusionSupport: null, occlusionSupported: true,  occlusionFeatures: '',
      occlusionComments: '',
      general: ''}, this.props.onClose())

  }
  render() {
    return (
          <Dialog isOpen={this.props.isOpen} title="Feedback"
            onClose={() =>    this.setState({othersModified: false, occlusionUseful: 3, occlusionSpeed: 3, occlusionSupport: null, occlusionSupported: true,  occlusionFeatures: '',
              occlusionComments: '',
              general: ''}, this.props.onClose())}
            style={{backgroundColor:"#F5F8FA"}}
            canEscapeClose={true}
            canOutsideClickClose={true}
            isCloseButtonShown={true}>

              <div style={{padding:10}} className="pt-dialog-body">
              If you want to submit feedback on how the tools analyse your current model and image selection, you can do so here. You can also submit any general feedback on the application itself.
              <form style={{marginTop:10}}>
              <h5>Occlusion Tool</h5>
               <Checkbox className="pt-align-right" name="occlusionSupported" checked={this.state.occlusionSupported} onChange={this.handleInputChange}>Was the occlusion tool able to support your image/model choice?</Checkbox>
              {(this.state.occlusionSupported) ? <div/> :<div><p>Which parts were unsupported?</p>
                <RadioGroup
                  name="occlusionSupport"
                  onChange={this.handleInputChange}
                  selectedValue={this.state.occlusionSupport}
                  >
                  <Radio label="Image" value="image" />
                  <Radio label="Model" value="model" />
                  <Radio label="Both" value="both" />
                  </RadioGroup></div>}
              <p>Was the occlusion tool useful? (1 being not useful at all and 5 being very useful)</p>
              <Slider onChange={this.occlusionUseful} min={1} max={5} initialValue={1} value={this.state.occlusionUseful}/>

              <p>How fast were the occlusions computed? (1 being very slow and 5 being not noticeable)</p>
              <Slider onChange={this.occlusionSpeed} min={1} max={5} initialValue={1} value={this.state.occlusionSpeed}/>

              <p>Was the occlusion tool able to pick out any interesting features from the image and model? Mention them below:</p>
              <textarea onChange={this.handleInputChange} name="occlusionFeatures" class="pt-input pt-fill" dir="auto"></textarea>
              <br/>

              <p>Do you have any other comments/suggestions for improvement of the occlusion tool?</p>
              <textarea onChange={this.handleInputChange} name="occlusionComments" class="pt-input pt-fill" dir="auto"></textarea>
              <br/>
              <br/>

              <h5>Synthesis Tool</h5>
              <Checkbox className="pt-align-right" name="synthesisSupported" checked={this.state.synthesisSupported} onChange={this.handleInputChange}>Was the synthesis tool able to support your image/model choice?</Checkbox>
             {(this.state.synthesisSupported) ? <div/> :<div><p>Which parts were unsupported?</p>
               <RadioGroup
                 name="synthesisSupport"
                 onChange={this.handleInputChange}
                 selectedValue={this.state.synthesisSupport}
                 >
                 <Radio label="Image" value="image" />
                 <Radio label="Model" value="model" />
                 <Radio label="Both" value="both" />
                 </RadioGroup></div>}

             <p>Was the synthesis tool useful? (1 being not useful at all and 5 being very useful)</p>
             <Slider onChange={this.synthesisUseful} min={1} max={5} initialValue={1} value={this.state.synthesisUseful}/>

             <p>How close were the synthesised features to the orignal features? (1 being not close at all and 5 being very close)</p>
             <Slider onChange={this.synthesisClose} min={1} max={5} initialValue={1} value={this.state.synthesisClose}/>

             <p>Was the synthesis tool able to pick out any interesting properties for these features? Mention them below:</p>
             <textarea onChange={this.handleInputChange} name="synthesisFeatures" class="pt-input pt-fill" dir="auto"></textarea>
             <br/>

              <p>Do you have any other comments/suggestions for improvement of the synthesis tool?</p>
              <textarea onChange={this.handleInputChange} name="synthesisComments" class="pt-input pt-fill" dir="auto"></textarea>
              <br/>
              <br/>
              <h5>General Comments</h5>
              If you have any other comments about the application, you can provide them here:<br/>
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
