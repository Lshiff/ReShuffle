from typing import List, Optional
from sqlalchemy import BIGINT, ForeignKey, create_engine, String, Date, TIMESTAMP, func, select, text, types, Integer, Boolean, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, Relationship, sessionmaker, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URI = os.getenv('DATABASE_URI')

if not DATABASE_URI:
    print("NO DATABASE URI")

connection_string = DATABASE_URI

engine = create_engine(connection_string, pool_recycle=500)#, echo=True) # resets connection every 4 minutes
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class Learner(Base):
    __tablename__ = "learners"
    id: Mapped[str] = mapped_column(String(), primary_key=True)
    full_name: Mapped[str] = mapped_column(String())
    instagram_handle: Mapped[str] = mapped_column(String())
    discord_username: Mapped[str] = mapped_column(String())
    email: Mapped[str] = mapped_column(String())
    status: Mapped[str] = mapped_column(String())
    school_id: Mapped[str] = mapped_column(UUID())
    teacher_id: Mapped[str] = mapped_column(UUID())
    grade: Mapped[int] = mapped_column()
    level: Mapped[int] = mapped_column()
    active_cycle: Mapped[int] = mapped_column()
    project_ids: Mapped[List[UUID]] = mapped_column(ForeignKey("projects.id"))
    current_project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))

    # projects: Mapped[List["Project"]] = relationship("Project", foreign_keys=project_ids, lazy="joined")#, back_populates="learner")
    current_project: Mapped["Project"] = relationship("Project", foreign_keys=[current_project_id], lazy="joined") #, back_populates="learner")

    # there's a lot more

    def __repr__(self):
        return f"""id: {self.id}
Full name: {self.full_name}
Instagram: {self.instagram_handle}
Discord: {self.discord_username}
Email: {self.email}
Project Ids: {self.project_ids}
Current Project Id: {self.current_project_id} """

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(UUID(), primary_key=True)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"))
    framework_id: Mapped[UUID] = mapped_column(UUID())
    learning_group_id: Mapped[UUID] = mapped_column(ForeignKey("learning_groups.id"))
    next_task_id: Mapped[UUID] = mapped_column(UUID())
    is_completed: Mapped[bool] = mapped_column(Boolean)

    learning_group: Mapped["LearningGroup"] = relationship(lazy="joined")

    def __repr__(self):
        return f"ID: {self.id}, learner_id: {self.learner_id}"

class LearningGroup(Base):
    __tablename__ = "learning_groups"

    id: Mapped[UUID] = mapped_column(UUID(), primary_key=True)
    quest_id: Mapped[str] = mapped_column(String())

    def __repr__(self):
        return f"ID: {self.id} | Quest: {self.quest_id}"


# class ModerationLog(Base):
#     __tablename__ = "moderation_logs"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP())
#     channel_id: Mapped[int] = mapped_column(BIGINT())
#     channel_name: Mapped[str] = mapped_column() 
#     moderation_category: Mapped[str] = mapped_column() 
#     moderation_message: Mapped[str] = mapped_column() 
#     sender_discord_id: Mapped[int] = mapped_column(BIGINT())
#     sender_discord_username: Mapped[str] = mapped_column() 

class SupportLog(Base):
    __tablename__ = "support_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column() 
    subcategory: Mapped[str] = mapped_column(nullable=True) 
    question: Mapped[str] = mapped_column() 
    message: Mapped[str] = mapped_column() 
    notes: Mapped[str] = mapped_column(nullable=True) 
    is_custom: Mapped[bool] = mapped_column(default=False)
    is_custom_category: Mapped[bool] = mapped_column(default=False)
    is_custom_question: Mapped[bool] = mapped_column(default=False)
    is_custom_message: Mapped[bool] = mapped_column(default=False)
    channel_id: Mapped[int] = mapped_column(BIGINT())
    channel_name: Mapped[str] = mapped_column() 
    original_message_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)
    original_message_content: Mapped[str] = mapped_column(nullable=True)
    original_message_sender_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)
    original_message_sender_discord_username: Mapped[str] = mapped_column(nullable=True) 
    sender_discord_id: Mapped[int] = mapped_column(BIGINT())
    sender_discord_username: Mapped[str] = mapped_column() 
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP())

    def __repr__(self):
        return f"""
ID: {self.id}
Category: {self.category}
Subcategory: {self.subcategory}
Question: {self.question}
Message: {self.message}
Notes: {self.notes}
Is Custom: {self.is_custom}
Is Custom Category: {self.is_custom_category}
Is Custom Question: {self.is_custom_question}
Is Custom Message: {self.is_custom_message}
Channel ID: {self.channel_id}
Channel Name: {self.channel_name}
Original Message ID: {self.original_message_id}
Original Message Content: {self.original_message_content}
Original Message Sender ID: {self.original_message_sender_id}
Original Message Sender Discord Username: {self.original_message_sender_discord_username}
Sender Discord ID: {self.sender_discord_id}
Sender Discord Username: {self.sender_discord_username}
Timestamp: {self.timestamp}
    """

class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    infraction: Mapped[str] = mapped_column() 
    message: Mapped[str] = mapped_column() 
    notes: Mapped[str] = mapped_column(nullable=True) 
    is_custom: Mapped[bool] = mapped_column(default=False)
    is_custom_infraction: Mapped[bool] = mapped_column(default=False)
    is_custom_message: Mapped[bool] = mapped_column(default=False)
    channel_id: Mapped[int] = mapped_column(BIGINT())
    channel_name: Mapped[str] = mapped_column() 
    original_message_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)
    original_message_content: Mapped[str] = mapped_column(nullable=True)
    original_message_sender_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)
    original_message_sender_discord_username: Mapped[str] = mapped_column(nullable=True) 
    sender_discord_id: Mapped[int] = mapped_column(BIGINT())
    sender_discord_username: Mapped[str] = mapped_column() 
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP())



class UserModerationLog(Base):
    __tablename__ = "user_moderation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP())
    user_discord_id: Mapped[int] = mapped_column(BIGINT())
    user_discord_username: Mapped[str] = mapped_column() 
    sender_discord_id: Mapped[int] = mapped_column(BIGINT())
    sender_discord_username: Mapped[str] = mapped_column() 
    punishment: Mapped[str] = mapped_column(nullable=True) 
    note: Mapped[str] = mapped_column() 

Base.metadata.create_all(engine)




def get_learner_from_discord(input_discord_username: str):
    with Session() as session:
        learner = session.query(Learner).filter_by(discord_username = input_discord_username).first()
    return learner


class DatabaseCommands:

    @staticmethod
    def get_current_quest_from_discord(discord_username: str):
        learner = get_learner_from_discord(discord_username)
        if not learner:
            return "No profile found"

        current_project = learner.current_project
        if not current_project:
            return "No current project"

        quest_name = current_project.learning_group.quest_id
        if not quest_name:
            return "No quest name"

        return quest_name

    # @staticmethod
    # def create_moderation_log(channel_id: int, channel_name: str, moderation_category: str, moderation_message: str, sender_discord_id: int, sender_discord_username: str):

    #     moderation_log = ModerationLog(
    #         timestamp = datetime.now(),
    #         channel_id = channel_id,
    #         channel_name = channel_name,
    #         moderation_category = moderation_category,
    #         moderation_message = moderation_message,
    #         sender_discord_id = sender_discord_id,
    #         sender_discord_username = sender_discord_username,
    #     )

    #     with Session() as session:
    #         session.add(moderation_log)
    #         session.commit()


    @staticmethod
    def create_moderation_log(
        *,
        infraction:str,
        message:str,
        notes: Optional[str] = None,
        is_custom:bool,
        is_custom_infraction:bool,
        is_custom_message:bool,
        channel_id:int,
        channel_name:str,
        sender_discord_id:int,
        sender_discord_username:str,
        original_message_id: Optional[int] = None,
        original_message_content: Optional[str] = None,
        original_message_sender_id: Optional[int] = None,
        original_message_sender_discord_username:Optional[str] = None
    ):

        moderation_log = ModerationLog(
            infraction = infraction,
            message = message,
            notes = notes,
            is_custom = is_custom,
            is_custom_infraction = is_custom_infraction,
            is_custom_message = is_custom_message,
            channel_id = channel_id,
            channel_name = channel_name,
            original_message_id = original_message_id,
            original_message_content = original_message_content,
            original_message_sender_id = original_message_sender_id,
            original_message_sender_discord_username = original_message_sender_discord_username,
            sender_discord_id = sender_discord_id,
            sender_discord_username = sender_discord_username,
            timestamp = datetime.now()
        )

        with Session() as session:
            session.add(moderation_log)
            session.commit()

    @staticmethod
    def create_support_log(
        *,
        category:str,
        subcategory:str,
        question:str,
        message:str,
        notes: Optional[str] = None,
        is_custom:bool,
        is_custom_category:bool,
        is_custom_question:bool,
        is_custom_message:bool,
        channel_id:int,
        channel_name:str,
        sender_discord_id:int,
        sender_discord_username:str,
        original_message_id: Optional[int] = None,
        original_message_content: Optional[str] = None,
        original_message_sender_id: Optional[int] = None,
        original_message_sender_discord_username:Optional[str] = None
    ) -> int:
        """
        Create a SupportLog with the given paramaters
        Return the support_log ID
        """

        support_log = SupportLog(
            category = category,
            subcategory = subcategory,
            question = question,
            message = message,
            notes = notes,
            is_custom = is_custom,
            is_custom_category = is_custom_category,
            is_custom_question = is_custom_question,
            is_custom_message = is_custom_message,
            channel_id = channel_id,
            channel_name = channel_name,
            original_message_id = original_message_id,
            original_message_content = original_message_content,
            original_message_sender_id = original_message_sender_id,
            original_message_sender_discord_username = original_message_sender_discord_username,
            sender_discord_id = sender_discord_id,
            sender_discord_username = sender_discord_username,
            timestamp = datetime.now()
        )

        with Session() as session:
            session.add(support_log)
            session.commit()

            print(f"returning id {support_log.id}")
            return support_log.id

    @staticmethod
    def update_support_log_notes(support_log_id: int, notes: str):
        with Session() as session:
            support_log = session.query(SupportLog).filter_by(id = support_log_id).first()
            if not support_log:
                return False
            support_log.notes = notes
            session.commit()
            return True

    @staticmethod
    def update_moderation_log_notes(moderation_log_id: int, notes: str):
        with Session() as session:
            moderation_log = session.query(ModerationLog).filter_by(id = moderation_log_id).first()
            if not moderation_log:
                return False
            moderation_log.notes = notes
            session.commit()
            return True

    @staticmethod
    def create_user_moderation_log(user_discord_id: int, user_discord_username: str, punishment: str, note: str, sender_discord_id: int, sender_discord_username: str):

        user_moderation_log = UserModerationLog(
            timestamp = datetime.now(),
            user_discord_id = user_discord_id,
            user_discord_username = user_discord_username,
            punishment = punishment,
            note = note,
            sender_discord_id = sender_discord_id,
            sender_discord_username = sender_discord_username,
        )

        with Session() as session:
            session.add(user_moderation_log)
            session.commit()

    @staticmethod
    def get_user_moderation_logs_by_discord_id(user_id: int):
        
        with Session() as session:
            notes = session.query(UserModerationLog).filter_by(user_discord_id = user_id).order_by(UserModerationLog.timestamp.desc()).all()

        return notes

if __name__ == "__main__":

    pass
    # print("hi")
    # print(DatabaseCommands.get_current_quest_from_discord("lshiff"))
