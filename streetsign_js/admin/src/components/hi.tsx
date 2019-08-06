import * as React from 'react';

export interface Props {
    name: string;
};

function Hi({name}: Props) {
    return (
        <div className="Ola">
            Hi {name}.
        </div>
    );
}

export default Hi;

// helpers?
