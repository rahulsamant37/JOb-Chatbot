import { CiLocationOn } from "react-icons/ci";
import { MdDateRange, MdOutlineUpdate } from "react-icons/md";
import { FaMoneyBill } from "react-icons/fa";
import { FaBuilding } from "react-icons/fa";
import { useTheme } from "../../../context/ThemeContext";

interface JobCardProps {
  title: string;
  company: string;
  duration?: string;
  location?: string;
  salary?: string;
  postedDate?: string;
  applyUrl?: string;
}

const timeAgo = (postedDate?: string) => {
  if (!postedDate) return "N/A";

  const postedTime = new Date(postedDate).getTime();
  const now = new Date().getTime();
  const diffInSeconds = Math.floor((now - postedTime) / 1000);

  //
  if (diffInSeconds < 0) return "N/A";
  if (diffInSeconds < 60) return `${diffInSeconds} sec ago`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min ago`;
  if (diffInSeconds < 86400)
    return `${Math.floor(diffInSeconds / 3600)} hr ago`;
  if (diffInSeconds < 2592000)
    return `${Math.floor(diffInSeconds / 86400)} day${
      Math.floor(diffInSeconds / 86400) == 1 ? "" : "s"
    } ago`;
  return new Date(postedDate).toLocaleDateString("en-US", {
    // weekday: "short", // "Mon"
    month: "short", // "Feb"
    day: "2-digit", // "04"
    year: "numeric", // "2024"
  });
};

const JobCard: React.FC<JobCardProps> = ({
  title,
  company,
  // duration,
  location,
  // salary,
  postedDate,
  applyUrl,
}) => {
  const { currentTheme } = useTheme();
  console.log(typeof timeAgo(postedDate));
  return (
    <div
      className="h-52 aspect-[330/310] rounded-2xl p-3 px-4.5 flex flex-col overflow-hidden"
      style={{ backgroundColor: currentTheme.jobCardBg }}
    >
      <div
        className="mb-3 text-left"
        style={{
          minHeight: "3rem", // Forces space for 2 lines
          display: "-webkit-box",
          WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
          color: currentTheme.primaryFont,
          fontWeight: "bold",
          fontSize: "1rem",
        }}
      >
        {title}
      </div>
      <p
        className="flex flex-row items-center gap-1 text-xs text-left mb-2"
        style={{ color: currentTheme.secondaryFont }}
      >
        <FaBuilding /> <span>{company}</span>
      </p>

      <div className="text-xs flex flex-col gap-1 mt-2">
        {location && (
          <div className="flex flex-row items-center gap-1">
            <CiLocationOn /> <span>{location}</span>
          </div>
        )}
        <div
          className="flex flex-row items-center gap-1"
          style={{ color: currentTheme.secondaryFont }}
        >
          <MdOutlineUpdate className="text-xs" />{" "}
          <span>{timeAgo(postedDate)}</span>
        </div>
      </div>

      <div className="flex-grow"></div>

      <div className="flex justify-between flex-none overflow-visible">
        <button
          className="cursor-pointer"
          style={{ color: currentTheme.applyButton }}
        >
          Details
        </button>
        <div
          className="w-[1px] h-6 opacity-50"
          style={{ backgroundColor: currentTheme.secondaryFont }}
        ></div>
        {applyUrl ? (
          <a
            href={applyUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="cursor-pointer"
            style={{ color: currentTheme.applyButton }}
          >
            Apply
          </a>
        ) : (
          <button className="cursor-not-allowed opacity-50" disabled>
            Apply
          </button>
        )}
      </div>
    </div>
  );
};

export default JobCard;
