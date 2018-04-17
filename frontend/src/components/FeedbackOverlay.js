import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'
import { Tab2, Tabs2 } from "@blueprintjs/core";
import PasswordMask from 'react-password-mask';

export default class FeedbackOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      general: '',
    };
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  isEmpty() {
    return this.state.general == ''
  }

  handleInputChange(event) {
   const target = event.target;
   const value = target.value;
   const name = target.name;

   this.setState({
     [name]: value
   });
 }

  submit() {
    fetch('/evaluation/', {
      method: 'POST',
      body: JSON.stringify({image: this.props.image.id, model:this.props.model.id, general: this.state.general}),
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
    this.props.onClose()
  }
  render() {
    return (
          <Dialog isOpen={this.props.isOpen} title="Feedback"
            onClose={() => this.setState({general: ''}, this.props.onClose())}
            style={{backgroundColor:"#F5F8FA"}}
            canEscapeClose={true}
            canOutsideClickClose={true}
            isCloseButtonShown={true}>

              <div className="pt-dialog-body">
              <form style={{padding:10}}>
              <h5>General Comments</h5>
              If you have any other comments about the application, you can provide them here.<br/>
              <textarea onChange={this.handleInputChange} name="general" class="pt-input pt-fill" dir="auto"></textarea>
              </form>
              </div>
              <div className="pt-dialog-footer" >
                             <div className="pt-dialog-footer-actions">
                             {(this.isEmpty()) ? <button type="button" className="pt-button pt-intent-primary pt-disabled">Submit</button>:
                             <button type="button" className="pt-button pt-intent-primary" onClick={() => this.submit()}>Submit</button>}
                             </div>
                         </div>
          </Dialog>
    );
  }
}
