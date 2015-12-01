#!/bin/sh

# FAIRBOT script to create SQL for playing Fairwinds
#
# Copyright 2015, Berend M. Tober
#

me=$(basename $0)
tmp=".${me}.$$"
touch "${tmp}"
trap 'rm "${tmp}"' EXIT
export COLUMNS=120
#export LINES=25
unset file

report="
\C 'Game Information'
with q as (select click, start_time, end_time, click_interval from fairwinds) select * from q order by click;
\C 'Recent Health Journal Entries'
with q as (select * from health_journal where fairian_name = current_user order by click desc limit 10) select click, fairian_name, debit, credit, balance, description from q order by click, seq;
\C 'Recent Cash Journal Entries'
with q as (select * from cash_journal   where fairian_name = current_user order by click desc limit 10) select click, fairian_name, debit, credit, balance, description from q order by click, seq;
\C 'Recent Food Journal Entries'
with q as (select * from food_journal   where fairian_name = current_user order by click desc limit 10) select click, fairian_name, debit, credit, balance, description  from q order by click, seq;
\C 'Bonds'
select * from bond where bond_owner = current_user or bond_issuer = current_user;
\C 'Land'
select * from land where fairian_name = current_user;
\C 'Labor Contracts'
select * from work where customer = current_user or supplier = current_user;
\C 'Notes'
select * from note where factor = current_user or debtor = current_user;
\C
"

  syntax=" \

USAGE: $me [options] host [username]  

CTRL-D to exit menus

Creates and runs SQL statements for placing trade orders in the Fairwinds game
running on specified host for Fairian username. Default username=${USER}.

OPTIONS

  -h
      Show help menu.

  "
  
if [ $# -lt 1 ]
then
  echo "${syntax}"
  exit
fi

while [ "$#" -gt 0 ]
do
  case $1 in
    -\?|-h)
      shift
      syntax
      exit
      ;;
    -*)
      echo "invalid option '${1}'"
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

fairian_name="${2-$USER}"
export PGDATABASE="fairwinds"
export PGHOST="${1}"
export PGUSER="${fairian_name}"


function executemenu {
  PS3="${2-$1} "
  select yn in "Execute" "Save" "Skip"
  do
    case "$yn" in
      Execute)
        psql -q <<< "${1}"
        ;;
      Save)
        read -p "Enter file name:" file
        echo "${1}" >> "${file}"
        ;;
      *)
        break
        ;;
    esac
    break
  done
  unset PS3
}

function createmenu {
  echo "Creating Fairain '${fairian_name}'"
  read -p "password=" password 
  read -p "email address=" email

  sql="insert into fairian (fairian_name, passwd, email_address) values ('${fairian_name}', '${password}', '${email}');"
  export PGUSER="fairwinds"
  executemenu "${sql}"
  export PGUSER="${fairian_name}"
}

function cultivatemenu {
  land_plots=$(psql -q -A -t <<< "select serial_number from land where fairian_name = current_user order by 1;")

  PS3="Select work place serial number "
  select serial_number in ${land_plots}
  do
    [[ -z "${serial_number}" ]] && break
    sql="insert into work (work_place, skill_name) values ('${serial_number}', 'farmer');"
    executemenu "${sql}"
  done
  unset PS3
}

function resignmenu {
  supplier_contracts=$(psql -q -A -t <<< "select contract_number from work where supplier = current_user order by 1;")

  PS3="Select labor contract number "
  select contract_number in ${supplier_contracts}
  do
    [[ -z "${contract_number}" ]] && break
    sql="update work set active = false where contract_number = '${contract_number}';"
    executemenu "${sql}"
    break
  done
  unset PS3
}

function optionsmenu {
  case "${1}" in
    bond)
      read -p "bond term=" term
      if [[ -n "${term}" ]]
      then
        fields="${fields}, term"
        values="${values}, ${term}"
      fi
      ;;
    land)
      case "${2}" in
        bid)
          read -p "land productivity=" productivity
          if [[ -n "${productivity}" ]]
          then
            fields="${fields}, productivity"
            values="${values}, ${productivity}"
          fi
          ;;
        ask)
          read -p "land serial number=" serial_number
          if [[ -n "${serial_number}" ]]
          then
            fields="${fields}, serial_number"
            values="${values}, '${serial_number}'"
          fi
          ;;
      esac
      ;;
    work)
        read -p "contract term=" term
        if [[ -n "${term}" ]]
        then
          fields="${fields}, term"
          values="${values}, ${term}"
        fi
        
      case "${2}" in
        bid)
          read -p "minimum effectiveness=" effectiveness
          if [[ -n "${effectiveness}" ]]
          then
            fields="${fields}, effectiveness"
            values="${values}, ${effectiveness}"
          fi

          read -p "work place serial number=" work_place
          if [[ -n "${work_place}" ]]
          then
            fields="${fields}, work_place"
            values="${values}, '${work_place}'"
          fi
          ;;
      esac

      fields="${fields}, skill_name"
      values="${values}, 'farmer'"
      ;;
    food)
      read -p "quantity=" quantity
      if [[ -n "${quantity}" ]]
      then
        fields="${fields}, quantity"
        values="${values}, ${quantity}"
      fi
      ;;
  esac
    
  if [[ -z "${fields}" ]]
  then
    sql="insert into ${mrkt}_${side} default values;"
  else
    sql="insert into ${mrkt}_${side} (${fields}) values (${values});"
  fi
  executemenu "${sql}"
}


function sidemenu {
  sides=("bid" "ask")
  unset side
  PS3="Buy (bid) or sell (ask)? "
  select side in "${sides[@]}"
  do
    case "${side}" in
      "bid"|"ask")
        read -p "expiration=" expiration
        if [[ -n "${expiration}" ]]
        then
          fields="expiration"
          values="${expiration}"
        else
          fields=""
        fi

        read -p "price=" price
        if [[ -n "${price}" ]]
        then
          fields="${fields}, price"
          values="${values}, ${price}"
        fi
        ;;
      *)
        break 
        ;;
    esac
    optionsmenu ${mrkt} ${side}
    break
  done
  unset PS3
}

function marketmenu {
  mrkts=("bond" "land" "work" "food" "note")
  unset mrkt
  PS3="Select market "
  select mrkt in "${mrkts[@]}"
  do
    case "${mrkt}" in
      "bond"|"land"|"work"|"food"|"note")
        sidemenu
        ;;
      *)
        break 
        ;;
    esac
    break
  done
  unset PS3
}

function mainmenu {
  options=("Create Fairian" "Trade" "Cultivate" "Resign" "Display")
  unset option
  select option in "${options[@]}"
  do
    case "${option}" in
      "Create Fairian")
        createmenu
        ;;
      "Trade")
        marketmenu
        ;;
      "Cultivate")
        cultivatemenu
        ;;
      "Resign")
        resignmenu
        ;;
      "Display")
        executemenu "${report}" "Run report?" 
        ;;
      *)
        break 
        ;;
    esac
  done
  unset PS3
}

mainmenu


