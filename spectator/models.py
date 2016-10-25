from sqlalchemy import (Column, DateTime, String, Integer, func, Boolean,
                        create_engine, ForeignKey, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

engine = create_engine('postgresql://localhost/spectator')
Session = sessionmaker(bind=engine)
session = Session()


class Descriptor(Base):  
    __tablename__ = 'descriptors'
    # Fields and comments from most relevant fields in:
    # https://stem.torproject.org/api/descriptor/server_descriptor.html

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    fingerprint = Column(String)
    published = Column(DateTime)  # time in UTC descriptor was made
    address = Column(String)  # IPv4 IP
    or_port = Column(Integer)  # port used for relaying
    dir_port = Column(Integer)  # port used for descriptor mirroring
    platform = Column(String)  # operating system and tor version
    tor_version = Column(String)  # version of tor
    operating_system = Column(String)  # os
    uptime = Column(Integer)  # uptime (seconds)
    contact = Column(String)  # contact information
    exit_policy = Column(String)  # stated exit policy
    exit_policy_v6 = Column(String)  # IPv6 exit policy
    family = Column(postgresql.ARRAY(String))  # nicknames / fingerprints of declared family
    average_bandwidth = Column(Integer)  # willing bandwidth (bytes/s)
    burst_bandwidth = Column(Integer)  # willing burst rate (bytes/s)
    observed_bandwidth = Column(Integer)  # estimated usage capacity (bytes/s)

    # link protocols supported by the relay
    link_protocols = Column(postgresql.ARRAY(String))
    # circuit protocols supported by the relay
    circuit_protocols = Column(postgresql.ARRAY(String))

    hibernating = Column(Boolean)  # hibernating when published
    allow_single_hop_exits = Column(Boolean)  # flag if single hop exiting is allowed
    allow_tunneled_dir_requests = Column(Boolean)  # flag if tunneled directory requests are accepted
    extra_info_cache = Column(Boolean)  # flag if a mirror for extra-info documents
    extra_info_digest = Column(String)  # upper-case hex encoded digest of our extra-info document

    # base64 key used to encrypt EXTEND in the ntor protocol
    ntor_onion_key  = Column(String)

    # alternative for our address/or_port attributes, each entry is
    # a tuple of the form (address (str), port (int), is_ipv6 (bool))
    or_addresses = Column(postgresql.ARRAY(String, dimensions=3))

    def __repr__(self):
        return 'Descriptor: ID {}, fingerprint {}'.format(self.id,
                                                          self.fingerprint)


class Scan(Base):
    __tablename__ = 'scans'
    # Table basically stores the scan

    id = Column(Integer, primary_key=True)
    submitter = Column(String)
    scan_type = Column(String)
    destination = Column(String)

    def __repr__(self):
        return 'Scan: ID {}, scan_type {}'.format(self.id, self.scan_type)


class ScanResult(Base):
    __tablename__ = 'scan_results'
    # Table basically stores individual results from scans

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id'))
    relay_id = Column(Integer, ForeignKey('descriptors.id'))
    t_scan = Column(DateTime)  # time the scan of this particular relay began
    anomalous = Column(Boolean)  # was an an anomaly found?
    anomaly_detail = Column(Text, nullable=True)

    def __repr__(self):
        return 'Scan Result: ID {}, anomalous {}'.format(self.id, self.anomalous)


def create():
    Base.metadata.create_all(engine)


if __name__=='__main__':
    