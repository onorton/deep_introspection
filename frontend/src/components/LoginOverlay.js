import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'
import { Tab2, Tabs2 } from "@blueprintjs/core";
import PasswordMask from 'react-password-mask';

export default class LoginOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      isOpen: false,
    };
  }

  componentWillReceiveProps(nextProps) {
    this.setState({isOpen:nextProps.isOpen})
  }

  componentWillMount() {
    const loginOverlay = this
    fetch('http://127.0.0.1:8000/accounts/login', {
      method: 'POST',
      body: JSON.stringify({username: this.state.username, password: this.state.password}),
      headers: {
          "Content-Type": "application/json"
      },
      credentials: "same-origin",
    }).then(function(response) {

      if (response.status == 200) {
        response.json().then(function(data) {
          loginOverlay.props.callbackParent(data.user)
          loginOverlay.setState({isOpen:false});
        })
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }


  login() {
    const loginOverlay = this
    const username = loginOverlay.state.username
    const password = loginOverlay.state.password
    loginOverlay.setState({username: '', password: ''})

    fetch('http://127.0.0.1:8000/accounts/login', {
      method: 'POST',
      body: JSON.stringify({username: username, password: password}),
      headers: {
          "Content-Type": "application/json"
      },
      credentials: "same-origin",
    }).then(function(response) {

      if (response.status == 200) {
        response.json().then(function(data) {
          loginOverlay.props.callbackParent(data.user)
          MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "Login Successful." });
          loginOverlay.setState({isOpen:false});

        })
      } else if (response.status == 400) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "Invalid username/password." });
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }
  signup() {
    const loginOverlay = this
    fetch('http://127.0.0.1:8000/accounts/', {
      method: 'POST',
      body: JSON.stringify({username: this.state.username, password: this.state.password}),
      headers: {
          "Content-Type": "application/json"
      },
      credentials: "same-origin",

    }).then(function(response) {

      if (response.status == 200) {
        response.json().then(function(data) {
          loginOverlay.props.callbackParent(data.user)
          MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "User created." });
          loginOverlay.setState({isOpen:false});

        })
      } else if (response.status == 409) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "This username already exists." });
      }

    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }
  render() {
    return (
          <Dialog isOpen={this.state.isOpen} title="Login"
            onClose={() => this.setState({isOpen:false})}
            style={{backgroundColor:"#F5F8FA"}}
            canEscapeClose={false}
            canOutsideClickClose={false}
            isCloseButtonShown={false}>

              <div className="pt-dialog-body">
              <p>In order to use Deep Introspection, you need to sign in first.</p>
              <Tabs2 id="loginTabs" onChange={this.handleTabChange}>
             <Tab2 id="log" title={<h5>Login</h5>} panel={
               <div>
               <h6>Username</h6>
               <input style={{marginBottom: 10, marginTop: 5}} value={this.state.username} onChange={evt => this.setState({username:evt.target.value})}/>
               <h6>Password</h6>
               <PasswordMask
                  style={{marginBottom: 10, marginTop: 5}}
                  id="password"
                  name="password"
                  value={this.state.password}
                  useVendorStyles={false}
                 onChange={evt => this.setState({password:evt.target.value})}
                />
               <label style={{marginTop: 10}} className="pt-button pt-active pt-intent-primary pt-icon-log-in" onClick={() => {this.login()}}>Login</label>
              </div>}/>
             <Tab2 id="sign" title={<h5>Sign Up</h5>} panel={
               <div>
               <h6>Username</h6>
               <input style={{marginBottom: 10, marginTop: 5}} value={this.state.username} onChange={evt => this.setState({username:evt.target.value})}/>
               <h6>Password</h6>
               <PasswordMask
                  style={{marginBottom: 10, marginTop: 5}}
                  id="password"
                  name="password"
                  value={this.state.password}
                  useVendorStyles={false}
                 onChange={evt => this.setState({password:evt.target.value})}
                />
               <label style={{marginTop: 10}} className="pt-button pt-active pt-intent-primary" onClick={() => {this.signup()}}>Sign Up</label>
              </div>}/>
             <Tabs2/>
          </Tabs2>
              </div>

          </Dialog>
    );
  }
}
