from typing import List, Optional
from sqlalchemy import BIGINT, ForeignKey, create_engine, String, Date, TIMESTAMP, func, select, text, types, Integer, Boolean, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, Relationship, sessionmaker, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from datetime import date, datetime, timedelta

# MySQL Configuration
mysql_host = 'reshuffle-db.c2ivaryam5yw.eu-central-1.rds.amazonaws.com'
mysql_user = 'postgres'
mysql_password = 'qeuurdmtwkspfyto'
mysql_db = 'reshuffle-staging'

POSTGRES_ADDR="postgresql+psycopg2://postgres:qeuurdmtwkspfyto@reshuffle-db.c2ivaryam5yw.eu-central-1.rds.amazonaws.com/reshuffle-staging"

connection_string = POSTGRES_ADDR

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


class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP())
    channel_id: Mapped[int] = mapped_column(BIGINT())
    channel_name: Mapped[str] = mapped_column() 
    moderation_category: Mapped[str] = mapped_column() 
    moderation_message: Mapped[str] = mapped_column() 
    sender_discord_id: Mapped[int] = mapped_column(BIGINT())
    sender_discord_username: Mapped[str] = mapped_column() 

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

    @staticmethod
    def create_moderation_log(channel_id: int, channel_name: str, moderation_category: str, moderation_message: str, sender_discord_id: int, sender_discord_username: str):

        moderation_log = ModerationLog(
            timestamp = datetime.now(),
            channel_id = channel_id,
            channel_name = channel_name,
            moderation_category = moderation_category,
            moderation_message = moderation_message,
            sender_discord_id = sender_discord_id,
            sender_discord_username = sender_discord_username,
        )

        with Session() as session:
            session.add(moderation_log)
            session.commit()

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

    # DatabaseCommands.create_moderation_log(
    #     channel_id = 1214938317141839906,
    #     channel_name = "general",
    #     moderation_category = "spam",
    #     moderation_message = "Feel free to talk here, but please don't spam!",
    #     sender_discord_id = 426195398210879498,
    #     sender_discord_username = "lshiff",
    # )

    notes = DatabaseCommands.get_user_moderation_logs_by_discord_id(265514761746120705)
    print(notes)

    # DatabaseCommands.create_user_moderation_log(
    #     user_discord_id = 426195398210879498,
    #     user_discord_username = "akiva",
    #     punishment = "",
    #     note = "He was bad",
    #     sender_discord_id = 426195398210879498,
    #     sender_discord_username = "lshiff",
    # )


    pass
    # print(get_learner_from_discord("kohvinleon"))
    # print(get_learner_from_discord("panjackflapcake"))

    # with Session() as session:
    #     lior = session.query(Learner).filter_by(id='212357983').first()
    #     if not lior:
    #         print("no lior (so sad)")
    #         exit()
    #     lior.discord_username = "lshiff"
    #     session.add(lior)
    #     session.commit()

    # print(get_current_quest_from_discord("kohvinleon"))
        # print("session yo")
        # learning_groups = session.query(LearningGroup).all()

    # for learning_group in learning_groups:
        # print(learning_group)
        # print(learner.projects)

# with Session() as session:
#     projects = session.query(Project).all()
# for project in projects:
#     print(project)
#     print(project.learning_group)


# with Session() as session:
#     learners = session.query(Learner).all()

# for learner in learners:
    # get_current_quest_from_discord("kohvinleon")
    # print(learner.full_name)
    # print(learner.discord_username)
    # # for project in learner.projects:
    # #     print(project.learning_group.quest_id)
    # current_project = learner.current_project
    # if current_project:
    #     learning_group = current_project.learning_group
    #     print(f"Current project: ")
    #     print(learning_group)
    # print()
    # print(learner)
    # print(learner.projects)
    # for project in learner.projects:
    #     print(project.learning_group)


# kohvinleon
# akivanagel_75126#0
