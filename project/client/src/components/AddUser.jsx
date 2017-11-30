import React from 'react';

const AddUser = props => {
  return (
    <form onSubmit={event => props.addUser(event)}>
      <div className="form-group">
        <input name="username" className="form-control input-lg" type="text" placeholder="Username" value={props.username} onChange={props.handleChange} required />
      </div>
      <div className="form-group">
        <input name="email" className="form-control input-lg" type="email" placeholder="Email" value={props.email} onChange={props.handleChange} required />
      </div>
      <input type="submit" className="btn btn-primary btn-lg btn-block" value="Signup" />
    </form>
  );
};

export default AddUser;