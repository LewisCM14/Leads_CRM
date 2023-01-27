import moment from 'moment';
import React, { useContext, useEffect, useState } from 'react';

import { UserContext } from '../context/UserContext';
import ErrorMessage from './ErrorMessage';
import LeadModal from './LeadModal';

const Table = () => {
	const [token] = useContext(UserContext);
	const [leads, setLeads] = useState(null);
	const [errorMessage, setErrorMessage] = useState('');
	const [loaded, setLoaded] = useState(false);
	const [activeModal, setActiveModal] = useState(false);
	const [id, setId] = useState(null);

	const getLeads = async () => {
		const requestOptions = {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Authorization: 'Bearer ' + token,
			},
		};
		const response = await fetch('/api/leads', requestOptions);

		if (!response.ok) {
			setErrorMessage('Something went wrong!');
		} else {
			const data = await response.json();
			setLeads(data);
			setLoaded(true);
		}
	};

	useEffect(() => {
		getLeads();
	}, []);

	const handleModal = () => {
		setActiveModal(!activeModal);
		getLeads();
		setActiveModal(null);
	};

	return (
		<>
			<LeadModal
				active={activeModal}
				handleModal={handleModal}
				token={token}
				id={id}
				setErrorMessage={setErrorMessage}
			/>
			<button
				className="button is-fullwidth mb-5 is-primary"
				onClick={() => setActiveModal(true)}
			>
				Create Lead
			</button>
			<ErrorMessage message={errorMessage} />
			{loaded && leads ? (
				<table className="table is-fullwidth">
					<thead>
						<tr>
							<th scope="col">First Name</th>
							<th scope="col">Last Name</th>
							<th scope="col">Company</th>
							<th scope="col">Email</th>
							<th scope="col">Notes</th>
							<th scope="col">Last Updated</th>
							<th scope="col">Actions</th>
						</tr>
					</thead>
					<tbody>
						{leads.map((lead) => (
							<tr key={lead.id}>
								<td>{lead.first_name}</td>
								<td>{lead.last_name}</td>
								<td>{lead.company}</td>
								<td>{lead.email}</td>
								<td>{lead.note}</td>
								<td>
									{moment(lead.date_last_updated).format(
										'MMM Do YY'
									)}
								</td>
								<td>
									<button className="button mr-2 is-info is-light">
										Update
									</button>
									<button className="button mr-2 is-danger is-light">
										Delete
									</button>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			) : (
				<p>Loading</p>
			)}
		</>
	);
};

export default Table;
